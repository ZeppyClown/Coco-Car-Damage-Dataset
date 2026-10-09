"""
Interactive Car Mechanic Assistant Application
"""
from src.rag_system import MechanicAssistant
from src.config import Config
import sys


class InteractiveMechanicApp:
    """Interactive command-line interface for mechanic assistant"""

    def __init__(self):
        print("Loading Car Mechanic Assistant...")
        try:
            self.assistant = MechanicAssistant()
            print("✓ Assistant ready!\n")
        except Exception as e:
            print(f"✗ Error initializing assistant: {e}")
            print("\nMake sure:")
            print("1. GOOGLE_API_KEY is set in .env")
            print("2. Vector database is built (run: python -m src.vector_store --output runtime/releases/initial)")
            sys.exit(1)

    def print_banner(self):
        """Print welcome banner"""
        print("="*80)
        print("CAR MECHANIC ASSISTANT - Powered by Google Gemini")
        print("="*80)
        print("\nAsk me anything about:")
        print("  • Vehicle diagnostics and troubleshooting")
        print("  • Fault code interpretation")
        print("  • Repair procedures and labor times")
        print("  • Parts identification and cross-references")
        print("  • Paint codes and specifications")
        print("  • Pricing and cost estimates")
        print("\nCommands:")
        print("  'exit' or 'quit' - Exit the application")
        print("  'help' - Show this message")
        print("  'verbose on/off' - Toggle verbose mode")
        print("  'clear' - Clear conversation")
        print("="*80 + "\n")

    def run(self):
        """Run interactive loop"""
        self.print_banner()

        verbose = False
        conversation_history = []

        while True:
            try:
                # Get user input
                user_input = input("\n🔧 You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ['exit', 'quit']:
                    print("\nGoodbye! 👋")
                    break

                elif user_input.lower() == 'help':
                    self.print_banner()
                    continue

                elif user_input.lower().startswith('verbose'):
                    if 'on' in user_input.lower():
                        verbose = True
                        print("✓ Verbose mode enabled")
                    else:
                        verbose = False
                        print("✓ Verbose mode disabled")
                    continue

                elif user_input.lower() == 'clear':
                    conversation_history = []
                    print("✓ Conversation cleared")
                    continue

                # Process query
                print("\n🤖 Assistant: ", end='', flush=True)

                result = self.assistant.query(user_input, verbose=verbose)

                if not verbose:
                    # Print response
                    print(result['response'])

                    # Print sources summary
                    if result['sources']:
                        print(f"\n📚 Sources: {', '.join(set(s['folder'] for s in result['sources']))}")

                # Save to conversation history
                conversation_history.append({
                    'query': user_input,
                    'response': result['response']
                })

            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break

            except Exception as e:
                print(f"\n✗ Error: {e}")
                print("Please try again or type 'help' for assistance.")


def main():
    """Main function"""
    app = InteractiveMechanicApp()
    app.run()


if __name__ == "__main__":
    main()
