from agent.graph import promptify

def main():
    """Main entry point for Promptify"""
    
    # Test input
    user_input = "I want to build a real-time chat application"
    
    # Initialize state
    initial_state = {
        "user_query": user_input,
        "intent": "",
        "critique": None,
        "expert_suggestions": "",
        "final_prompt_draft": "",
        "iteration_count": 0
    }
    
    print("🚀 Promptify Agent Starting...")
    print(f"📝 User Query: {user_input}\n")
    
    # Run the graph
    result = promptify.invoke(initial_state)
    
    # Display results
    print("=" * 80)
    print(f"🎯 Detected Intent: {result['intent']}")
    print("=" * 80)
    print(f"\n🔍 Critique:\n{result['critique']}\n")
    print("=" * 80)
    print(f"\n💡 Expert Suggestions:\n{result['expert_suggestions']}\n")
    print("=" * 80)
    print(f"\n✨ Final Refined Prompt:\n{result['final_prompt_draft']}\n")
    print("=" * 80)

if __name__ == "__main__":
    main()
