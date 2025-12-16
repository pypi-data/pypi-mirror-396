"""Text statistics command-line tool."""
import sys


def show_usage():
    """Display usage instructions for the tool."""
    usage_message = """Usage: myproject [OPTIONS] <filename>

Calculate statistics for a text file.

Arguments:
  <filename>    Path to the text file to analyze

Options:
  --help        Show this help message
  --output FILE Write results to FILE instead of printing

Examples:
  myproject myfile.txt
  myproject --output results.txt myfile.txt
"""
    print(usage_message)


def count_text_stats(text):
    """Count lines, words, and characters in text.
    
    Arguments:
        text: String containing the text to analyze
        
    Returns:
        Dictionary with 'lines', 'words', and 'chars' counts
    """
    lines = text.splitlines()
    words = text.split()
    chars = len(text)
    
    return {
        "lines": len(lines),
        "words": len(words),
        "chars": chars
    }


def format_stats(stats):
    """Format statistics as a readable string.
    
    Argumentss:
        stats: Dictionary with 'lines', 'words', 'chars' keys
        
    Returns:
        Formatted string like "5 lines, 56 words, 193 characters"
    """
    return f"{stats['lines']} lines, {stats['words']} words, {stats['chars']} characters"


def read_file(filename):
    """Read and return contents of a file.
    
    Arguments:
        filename: Path to file to read
        
    Returns:
        String containing file contents
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def write_file(filename, content):
    """Write content to a file.
    
    Arguments:
        filename: Path to file to write
        content: String to write to file
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """Main entry point for the CLI tool."""
    args = sys.argv[1:]  # Get command-line arguments 
    
    # Show help if no arguments or --help flag
    if not args or "--help" in args or "-h" in args:
        show_usage()
        return
    
    # Parse arguments
    output_file = None
    input_file = None
    
    i = 0
    while i < len(args):
        if args[i] == "--output":
            # Next argument should be the output filename
            if i + 1 < len(args):
                output_file = args[i + 1]
                i += 2  # Skip both --output and the filename
            else:
                print("Error: --output requires a filename")
                show_usage()
                return
        else:
            # This should be the input file
            input_file = args[i]
            i += 1
    
    # Validate that we have an input file
    if not input_file:
        print("Error: No input file specified")
        show_usage()
        return
    
    # Try to read and analyze the file
    try:
        text = read_file(input_file)
        stats = count_text_stats(text)
        result = format_stats(stats)
        
        # Output results
        if output_file:
            write_file(output_file, result)
            print(f"Results written to {output_file}")
        else:
            print(result)
            
    # Error catching block        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        print("Please check the filename and try again.")
    except PermissionError:
        print(f"Error: Permission denied when accessing '{input_file}'")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
