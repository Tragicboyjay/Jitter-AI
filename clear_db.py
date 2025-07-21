import argparse
from memory.sqlite_actions import clear_all_messages, clear_messages_by_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clear messages from the database.")
    parser.add_argument("--context_id", type=str, default=None, help="Context ID to clear messages for (if omitted, clears all messages)")
    args = parser.parse_args()

    if args.context_id:
        print(f"Clearing messages for context_id: {args.context_id}...")
        clear_messages_by_id(args.context_id)
        print(f"Messages for context_id {args.context_id} cleared.")
    else:
        print("Clearing all messages from the database...")
        clear_all_messages()
        print("All messages cleared.")
