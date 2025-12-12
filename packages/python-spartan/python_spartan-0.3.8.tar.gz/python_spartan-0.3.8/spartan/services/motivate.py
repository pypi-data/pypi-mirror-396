import random


class MotivateService:
    def __init__(self):
        self.quotes = [
            {
                "quote": "The only way to do great work is to love what you do.",
                "author": "Steve Jobs",
            },
            {
                "quote": "Simplicity is the soul of efficiency.",
                "author": "Austin Freeman",
            },
            {
                "quote": "Programming is thinking, not typing.",
                "author": "Casey Patton",
            },
            {
                "quote": "The best code is no code at all.",
                "author": "Jeff Atwood",
            },
            {
                "quote": "Coding is not just code; it's about making things happen.",
                "author": "Adam Timčo",
            },
            {
                "quote": "In software development, the best code is no code at all.",
                "author": "Jeff Atwood",
            },
            {
                "quote": "The most important skill for a software engineer is problem-solving. Everything else can be learned.",
                "author": "Unknown",
            },
            {
                "quote": "Software developers are the architects of the digital world.",
                "author": "Unknown",
            },
            {
                "quote": "Coding is not just a job; it's a way of life.",
                "author": "Unknown",
            },
            {
                "quote": "The best way to predict the future is to create it.",
                "author": "Alan Kay",
            },
            {
                "quote": "A program is never less than 90% complete, and never more than 95% complete.",
                "author": "Terry Baker",
            },
            {
                "quote": "You can't trust code that you did not totally create yourself.",
                "author": "Ken Thompson",
            },
            {
                "quote": "Code refactoring is like doing the dishes; it's never done, but doing it regularly makes life better.",
                "author": "Unknown",
            },
            {
                "quote": "The computer programmer is a creator of universes for which they alone are the lawgiver.",
                "author": "Joseph Weizenbaum",
            },
            {
                "quote": "Programming languages shape the way we think.",
                "author": "Larry Wall",
            },
            {
                "quote": "It's not about the language you use; it's about the problems you solve.",
                "author": "Larry Wall",
            },
            {
                "quote": "The best software developers are the ones who think like the users.",
                "author": "Jeff Atwood",
            },
            {
                "quote": "Good code is its own best documentation.",
                "author": "Steve McConnell",
            },
        ]

    def get_random_quote(self):
        random_quote = random.choice(self.quotes)
        return f'"{random_quote["quote"]}" - {random_quote["author"]}'
