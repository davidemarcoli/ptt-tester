#!/usr/bin/env python3
"""
Torrent Parser Testing Tool

This script helps test the PTT (Parse Torrent Title) library against a dataset of torrent titles or a single title.
It either parses a single provided title or randomly selects titles from a dataset, parses them,
and asks for user feedback on parsing accuracy. Results are saved to allow for retesting with updated
library versions.
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from PTT import parse_title


class TorrentTester:
    def __init__(self, dataset_path: Optional[str], results_path: str, library_version: str):
        """
        Initialize the TorrentTester.

        Args:
            dataset_path: Path to the text file containing torrent titles, or None if single title mode
            results_path: Path to save the test results
            library_version: Version of the parsing library being tested
        """
        self.dataset_path = dataset_path
        self.results_path = results_path
        self.library_version = library_version
        self.results = self._load_results()
        self.torrent_titles = self._load_dataset() if dataset_path else []
        
    def _load_dataset(self) -> List[str]:
        """Load torrent titles from the dataset file."""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                # Strip whitespace and filter out empty lines
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Error loading dataset: {e}")
            sys.exit(1)
            
    def _load_results(self) -> Dict:
        """Load existing test results if available."""
        if os.path.exists(self.results_path):
            try:
                with open(self.results_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Results file is corrupted. Creating backup and starting fresh.")
                self._backup_results()
                return self._create_new_results()
        else:
            return self._create_new_results()
            
    def _create_new_results(self) -> Dict:
        """Create a new results structure."""
        return {
            "versions": {},
            "titles": {}
        }
        
    def _backup_results(self):
        """Create a backup of the results file."""
        if os.path.exists(self.results_path):
            backup_path = f"{self.results_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            try:
                os.rename(self.results_path, backup_path)
                print(f"Backup created at {backup_path}")
            except Exception as e:
                print(f"Failed to create backup: {e}")
                
    def save_results(self):
        """Save current results to file."""
        try:
            with open(self.results_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2)
        except Exception as e:
            print(f"Error saving results: {e}")
            
    def get_random_untested_title(self) -> Optional[str]:
        """
        Get a random torrent title that hasn't been tested with the current library version.
        Returns None if all titles have been tested.
        """
        untested_titles = [
            title for title in self.torrent_titles 
            if title not in self.results["titles"] or 
            self.library_version not in self.results["titles"][title]
        ]
        
        if not untested_titles:
            return None
            
        return random.choice(untested_titles)
        
    def parse_torrent_title(self, title: str) -> Dict:
        """
        Parse a torrent title using the imported library.
        
        Args:
            title: The torrent title to parse
            
        Returns:
            The parsed result as a dictionary
        """
        return parse_title(title)
        
    def record_result(self, title: str, parsed_result: Dict, is_correct: bool, notes: str = ""):
        """
        Record the test result for a torrent title.
        
        Args:
            title: The torrent title
            parsed_result: The result from the parser
            is_correct: Whether the parsing was correct
            notes: Optional notes about the result
        """
        # Initialize version entry if it doesn't exist
        if self.library_version not in self.results["versions"]:
            self.results["versions"][self.library_version] = {
                "tested_count": 0,
                "correct_count": 0,
                "timestamp": datetime.now().isoformat()
            }
            
        # Initialize title entry if it doesn't exist
        if title not in self.results["titles"]:
            self.results["titles"][title] = {}
            
        # Record result for this version
        self.results["titles"][title][self.library_version] = {
            "is_correct": is_correct,
            "parsed_result": parsed_result,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update version statistics
        self.results["versions"][self.library_version]["tested_count"] += 1
        if is_correct:
            self.results["versions"][self.library_version]["correct_count"] += 1
            
        # Save after each result to prevent data loss
        self.save_results()
        
    def get_previously_tested_titles(self) -> List[str]:
        """Get a list of all previously tested titles."""
        return list(self.results["titles"].keys())
        
    def print_statistics(self):
        """Print statistics about testing progress."""
        if not self.torrent_titles:  # Skip stats in single title mode
            return
            
        total_titles = len(self.torrent_titles)
        tested_this_version = 0
        correct_this_version = 0
        
        if self.library_version in self.results["versions"]:
            version_stats = self.results["versions"][self.library_version]
            tested_this_version = version_stats["tested_count"]
            correct_this_version = version_stats["correct_count"]
            
        total_tested_titles = len(self.results["titles"])
        
        print("\n===== Testing Statistics =====")
        print(f"Library version: {self.library_version}")
        print(f"Total titles in dataset: {total_titles}")
        print(f"Total titles tested (any version): {total_tested_titles}")
        print(f"Titles tested with current version: {tested_this_version}")
        
        if tested_this_version > 0:
            accuracy = (correct_this_version / tested_this_version) * 100
            print(f"Current version accuracy: {accuracy:.2f}%")
            
        untested_count = len([
            title for title in self.torrent_titles 
            if title not in self.results["titles"] or 
            self.library_version not in self.results["titles"][title]
        ])
        print(f"Untested titles with current version: {untested_count}")
        print("=============================\n")


def parse_single_title(title: str, tester: TorrentTester, save_result: bool = False):
    """
    Parse a single torrent title and display results.
    
    Args:
        title: The torrent title to parse
        tester: The TorrentTester instance
        save_result: Whether to save the result to the results file
    """
    # Parse the title
    parsed_result = tester.parse_torrent_title(title)
    
    # Display the original title and parsed result
    print("\n" + "="*80)
    print(f"Title: {title}")
    print("-"*80)
    print("Parsed Result:")
    for key, value in parsed_result.items():
        print(f"  {key}: {value}")
    print("-"*80)
    
    if save_result:
        # Get user feedback
        while True:
            response = input("Is this parsing correct? (Y/n/s/q) [Y=yes, n=no, s=skip, q=quit]: ").lower()
            if response in ['y', 'n', 's', 'q', '']:
                break
            print("Invalid input. Please enter Y, n, s or q (or press Enter for Yes).")
            
        if response == 'q':
            print("Quitting test session.")
            return
            
        if response == 's':
            print("Skipping this title.")
            return
            
        is_correct = (response == 'y' or response == '')
        
        # Only ask for notes if the parsing was incorrect
        notes = ""
        if not is_correct:
            notes = input("Notes about this result: ")
        
        # Record the result
        tester.record_result(title, parsed_result, is_correct, notes)
    
  
def interactive_testing(tester: TorrentTester, retest_mode: bool = False):
    """
    Run interactive testing session.
    
    Args:
        tester: The TorrentTester instance
        retest_mode: If True, retest previously tested titles
    """
    try:
        if retest_mode:
            titles_to_test = tester.get_previously_tested_titles()
            if not titles_to_test:
                print("No previously tested titles found.")
                return
            random.shuffle(titles_to_test)
        else:
            titles_to_test = []  # Will be selected one by one
            
        count = 0
        while True:
            if retest_mode and count >= len(titles_to_test):
                print("All previously tested titles have been retested.")
                break
                
            if retest_mode:
                title = titles_to_test[count]
            else:
                title = tester.get_random_untested_title()
                if not title:
                    print("All titles in the dataset have been tested with this library version.")
                    break
                    
            # Parse the title
            parsed_result = tester.parse_torrent_title(title)
            
            # Display the original title and parsed result
            print("\n" + "="*80)
            print(f"Title: {title}")
            print("-"*80)
            print("Parsed Result:")
            for key, value in parsed_result.items():
                print(f"  {key}: {value}")
            print("-"*80)
            
            # Get user feedback with Y as default
            while True:
                response = input("Is this parsing correct? (Y/n/s/q) [Y=yes, n=no, s=skip, q=quit]: ").lower()
                if response in ['y', 'n', 's', 'q', '']:
                    break
                print("Invalid input. Please enter Y, n, s or q (or press Enter for Yes).")
                
            if response == 'q':
                print("Quitting test session.")
                break
                
            if response == 's':
                print("Skipping this title.")
                count += 1
                continue
                
            is_correct = (response == 'y' or response == '')
            
            # Only ask for notes if the parsing was incorrect
            notes = ""
            if not is_correct:
                notes = input("Notes about this result: ")
            
            # Record the result
            tester.record_result(title, parsed_result, is_correct, notes)
            
            count += 1
            
            # Display statistics periodically
            if count % 5 == 0:
                tester.print_statistics()
                
            # Ask to continue
            if count % 10 == 0:
                continue_response = input("Continue testing? (Y/n): ").lower()
                if continue_response not in ['', 'y']:
                    print("Ending test session.")
                    break
                    
    except KeyboardInterrupt:
        print("\nTest session interrupted.")
    finally:
        # Save results one last time
        tester.save_results()
        tester.print_statistics()
        

def main():
    parser = argparse.ArgumentParser(description="Interactive torrent title parser tester")
    parser.add_argument("dataset", nargs='?', default=None,
                        help="Path to the text file containing torrent titles (optional)")
    parser.add_argument("--title", "-t", default=None,
                        help="Process a single torrent title instead of reading from a file")
    parser.add_argument("--results", default="parser_test_results.json", 
                        help="Path to save test results (default: parser_test_results.json)")
    parser.add_argument("--version", default="dev", 
                        help="Version of the parser being tested (default: dev)")
    parser.add_argument("--retest", action="store_true", 
                        help="Retest previously tested titles")
    parser.add_argument("--stats", action="store_true", 
                        help="Print statistics and exit")
    parser.add_argument("--save", "-s", action="store_true",
                        help="Save result when testing a single title")
    
    args = parser.parse_args()
    
    # Check if we have either a dataset or a single title
    if args.dataset is None and args.title is None:
        parser.error("Either a dataset file or a single title (--title) is required")
    
    # Create the tester instance
    tester = TorrentTester(args.dataset, args.results, args.version)
    
    # Handle single title mode
    if args.title:
        parse_single_title(args.title, tester, args.save)
        return
    
    # Stats only mode
    if args.stats:
        tester.print_statistics()
        return
    
    # Dataset testing mode    
    print(f"Testing parser version: {args.version}")
    print(f"Dataset: {args.dataset}")
    print(f"Results will be saved to: {args.results}")
    
    if args.retest:
        print("Mode: Retesting previously tested titles")
    else:
        print("Mode: Testing new random titles")
        
    input("Press Enter to begin testing...")
    
    interactive_testing(tester, retest_mode=args.retest)
    

if __name__ == "__main__":
    main()