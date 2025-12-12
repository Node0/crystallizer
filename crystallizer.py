#!/usr/bin/env python3
"""
Crystallizer: LLM-powered text synthesis with token-aware windowing.
Handles arbitrary text files/folders, provider-agnostic LLM backends.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Protocol

import tiktoken
from jinja2 import Template
import time

from utilities import Print
from backends.providers import get_provider_class


class LLMProvider(Protocol):
    def generate(self, system_prompt: str, user_content: str) -> str:
        ...


class TokenCounter:
    def __init__(self, encoding_name: str = "cl100k_base"):
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def chunk_text(self, text: str, max_tokens: int, overlap: int = 100) -> List[str]:
        """Split text into chunks that fit within token limits."""
        tokens = self.encoding.encode(text)
        chunks = []
        start = 0
        while start < len(tokens):
            end = min(start + max_tokens, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            chunks.append(chunk_text)
            if end >= len(tokens):
                break
            start = end - overlap
        return chunks


class Crystallizer:
    def __init__(self, config_path: str, connection_name: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        connections = self.config.get("inference_service_connections", {})
        if not connections:
            raise ValueError("Config file missing 'inference_service_connections'")
        if connection_name not in connections:
            raise ValueError(f"Connection '{connection_name}' not found in config")

        self.connection_name = connection_name
        self.connection_config = connections[connection_name]
        self.api_type = self.connection_config.get("api_type")
        if not self.api_type:
            raise ValueError(f"Connection '{connection_name}' missing 'api_type'")

        provider_class = get_provider_class(self.api_type)
        self.provider = provider_class(self.connection_config)

        self.context_length = self.connection_config.get("default_ctx_len", 16000)
        self.token_counter = TokenCounter()

    def load_system_prompt(self, template_path: str, **kwargs) -> str:
        """Load and render Jinja2 system prompt template."""
        with open(template_path, 'r') as f:
            template = Template(f.read())
        return template.render(**kwargs)

    def create_filename(self, base_name: str, task_label: str, ordinal: int = None) -> str:
        """Create deterministic filename: <base>__<task>__NNN.txt"""
        if ordinal is not None:
            return f"{base_name}__{task_label}__{ordinal:03d}.txt"
        else:
            return f"{base_name}__{task_label}__final.txt"

    def parse_filename(self, filename: str) -> tuple:
        """Parse filename back into components."""
        name = Path(filename).stem
        parts = name.split("__")
        if len(parts) >= 3:
            base_name = parts[0]
            task_label = parts[1]
            ordinal_or_final = parts[2]
            return base_name, task_label, ordinal_or_final
        return None, None, None

    def process_single_window(self, content: str, system_prompt: str,
                              base_name: str, task_label: str,
                              window_idx: int, output_dir: Path) -> List[str]:
        """Process a single window with 3-segment strategy."""
        Print("STARTING", f"Window {window_idx}: 3-segment processing")
        crystals = []
        segment_size = len(content) // 3
        segments = [
            content[:segment_size],
            content[segment_size:segment_size * 2],
            content[segment_size * 2:]
        ]
        for seg_idx, segment in enumerate(segments):
            if not segment.strip():
                continue
            Print("PROGRESS", f"Window {window_idx}, segment {seg_idx + 1}/3")
            try:
                Print("ATTEMPT", f"LLM generation for segment {seg_idx}")
                result = self.provider.generate(system_prompt, segment)
                ordinal = window_idx * 3 + seg_idx
                crystal_filename = self.create_filename(base_name, task_label, ordinal)
                crystal_path = output_dir / crystal_filename
                with open(crystal_path, 'w') as f:
                    f.write(result)
                crystals.append(str(crystal_path))
                Print("SUCCESS", f"Generated crystal: {crystal_filename}")
                time.sleep(0.1)
            except Exception as e:
                Print("EXCEPTION", f"Failed to process segment {seg_idx} of window {window_idx}: {e}")
        Print("COMPLETED", f"Window {window_idx}: Generated {len(crystals)} crystals")
        return crystals

    def merge_crystals(self, crystal_paths: List[str], system_prompt: str,
                       base_name: str, task_label: str, output_dir: Path) -> str:
        """Merge all crystals into final output."""
        if not crystal_paths:
            return None
        Print("STARTING", f"Merging {len(crystal_paths)} crystals")
        crystal_contents = []
        for idx, path in enumerate(sorted(crystal_paths)):
            Print("PROGRESS", f"Reading crystal {idx + 1}/{len(crystal_paths)}")
            with open(path, 'r') as f:
                crystal_contents.append(f.read())
        merge_prompt = f"""You are merging {len(crystal_contents)} crystallized segments in chronological order.
Combine them into a single, coherent, deduplicated summary while preserving:
- Chronological ordering
- Evolution of ideas (mark v1, v2, etc. if concepts evolve)
- All key decisions and architectural insights
- Remove redundancy but keep completeness

Output should be well-structured and comprehensive."""
        combined_content = "\n\n--- CRYSTAL SEGMENT ---\n\n".join(crystal_contents)
        try:
            Print("ATTEMPT", f"LLM merge of {len(crystal_contents)} segments")
            final_result = self.provider.generate(merge_prompt, combined_content)
            final_filename = self.create_filename(base_name, task_label)
            final_path = output_dir / final_filename
            with open(final_path, 'w') as f:
                f.write(final_result)
            Print("COMPLETED", f"Final crystal merge: {final_filename}")
            return str(final_path)
        except Exception as e:
            Print("EXCEPTION", f"Failed to merge crystals: {e}")
            return None

    def process_file(self, file_path: Path, system_prompt: str,
                     task_label: str, output_dir: Path) -> str:
        """Process a single text file."""
        Print("INFO", f"Processing: {file_path.name}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            Print("WARNING", f"Skipping binary file: {file_path}")
            return None
        base_name = file_path.stem
        token_count = self.token_counter.count_tokens(content)
        Print("INFO", f"Token count: {token_count:,}")
        safe_window = max(2000, self.context_length - 2000)
        all_crystals = []
        if token_count <= safe_window:
            Print("INFO", "Single window processing")
            crystals = self.process_single_window(
                content, system_prompt, base_name, task_label, 0, output_dir
            )
            all_crystals.extend(crystals)
        else:
            num_windows = token_count // safe_window + 1
            Print("INFO", f"Multi-window processing ({num_windows} windows)")
            Print("STARTING", f"Chunking {token_count:,} tokens into {num_windows} windows")
            chunks = self.token_counter.chunk_text(content, safe_window)
            for window_idx, chunk in enumerate(chunks):
                Print("PROGRESS", f"Processing window {window_idx + 1}/{len(chunks)}")
                crystals = self.process_single_window(
                    chunk, system_prompt, base_name, task_label, window_idx, output_dir
                )
                all_crystals.extend(crystals)
        final_crystal = self.merge_crystals(
            all_crystals, system_prompt, base_name, task_label, output_dir
        )
        Print("STATE", f"Cleaning up {len(all_crystals)} intermediate crystal files")
        for crystal_path in all_crystals:
            try:
                os.remove(crystal_path)
            except OSError:
                pass
        return final_crystal

    def process_haystack(self, haystack_path: str, system_prompt_template: str,
                         task_label: str, output_dir: str) -> List[str]:
        """Main processing function."""
        haystack = Path(haystack_path)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        system_prompt = self.load_system_prompt(
            system_prompt_template,
            task_label=task_label,
            provider=self.api_type,
            connection=self.connection_name,
        )
        final_crystals = []
        if haystack.is_file():
            result = self.process_file(haystack, system_prompt, task_label, output_path)
            if result:
                final_crystals.append(result)
        elif haystack.is_dir():
            text_files = [f for f in haystack.rglob("*.txt") if f.is_file()]
            text_files.extend([f for f in haystack.rglob("*.md") if f.is_file()])
            Print("INFO", f"Found {len(text_files)} text files")
            Print("STARTING", f"Batch processing {len(text_files)} files")
            for file_idx, file_path in enumerate(sorted(text_files)):
                Print("PROGRESS", f"File {file_idx + 1}/{len(text_files)}: {file_path.name}")
                result = self.process_file(file_path, system_prompt, task_label, output_path)
                if result:
                    final_crystals.append(result)
            Print("COMPLETED", f"Batch processing finished")
        else:
            Print("FAILURE", f"Haystack path not found: {haystack_path}")
            raise ValueError(f"Haystack path not found: {haystack_path}")
        Print("SUCCESS", f"Generated {len(final_crystals)} final crystals in {output_path}")
        return final_crystals


def main():
    parser = argparse.ArgumentParser(description="Crystallizer: LLM-powered text synthesis")
    parser.add_argument("--system-prompt", required=True,
                        help="Path to Jinja2 system prompt template")
    parser.add_argument("--haystack-path", required=True,
                        help="Path to text file or directory")
    parser.add_argument("--connection", "--provider", dest="connection_name", required=True,
                        help="Name of the inference_service_connections entry to use")
    parser.add_argument("--config-file-path", default="./config/config.json",
                        help="Path to config file")
    parser.add_argument("--output-dir", default="./crystals",
                        help="Output directory for crystals")
    parser.add_argument("--task-label", default="crystal",
                        help="Task identifier for filenames")
    args = parser.parse_args()

    try:
        Print("STARTING", "Initializing crystallizer")
        crystallizer = Crystallizer(args.config_file_path, args.connection_name)
        Print("STATE", f"System prompt: {args.system_prompt}")
        Print("STATE", f"Connection: {crystallizer.connection_name} ({crystallizer.api_type})")
        Print("STATE", f"Task label: {args.task_label}")
        crystals = crystallizer.process_haystack(
            args.haystack_path,
            args.system_prompt,
            args.task_label,
            args.output_dir
        )
        Print("SUCCESS", "Crystallization complete!")
        Print("INFO", f"Output directory: {args.output_dir}")
    except Exception as e:
        Print("EXCEPTION", f"Crystallization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
