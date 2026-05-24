"""
Budget Quest - Gamified Budget Tracker

Main file to run:
    python3 budget_quest.py

This program is a simple student budget tracker with gamified feedback.
It uses only Python built-in libraries, saves data to a JSON file, and
demonstrates object-oriented programming, file handling, dictionaries,
lists, validation, date handling, and conditional logic.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


# Save the JSON data file beside the program file.
DATA_FILE = Path(__file__).with_name("budget_records.json")

# The user chooses one category for each expense record.
CATEGORIES = [
    "Food",
    "Transport",
    "Study",
    "Shopping",
    "Entertainment",
    "Health",
    "Other",
]

ESSENTIAL_CATEGORIES = {"Food", "Transport", "Study", "Health"}
# These optional spending categories affect the Budget Score rules.
NON_ESSENTIAL_CATEGORIES = {"Shopping", "Entertainment"}


@dataclass
class Expense:
    """Represents one spending record."""

    record_id: int
    expense_date: str
    category: str
    amount: float
    description: str

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "expense_date": self.expense_date,
            "category": self.category,
            "amount": self.amount,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        return cls(
            record_id=int(data["record_id"]),
            expense_date=str(data["expense_date"]),
            category=str(data["category"]),
            amount=float(data["amount"]),
            description=str(data.get("description", "")),
        )


class BudgetQuest:
    """Stores expenses and calculates game-style budget feedback."""

    def __init__(self) -> None:
        self.expenses: list[Expense] = []
        self.target_budget: float | None = None

    def load(self) -> None:
        # If there is no saved JSON file yet, start with empty records.
        if not DATA_FILE.exists():
            return

        try:
            with DATA_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            print("Warning: Existing data file could not be read. Starting fresh.")
            return

        self.target_budget = data.get("target_budget")
        self.expenses = [
            Expense.from_dict(item) for item in data.get("expenses", [])
        ]

    def save(self) -> None:
        # Convert the current budget target and records into JSON data.
        data = {
            "target_budget": self.target_budget,
            "expenses": [expense.to_dict() for expense in self.expenses],
        }
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def next_id(self) -> int:
        if not self.expenses:
            return 1
        return max(expense.record_id for expense in self.expenses) + 1

    def add_expense(
        self, expense_date: str, category: str, amount: float, description: str
    ) -> Expense:
        # Give every new expense an ID so it can be displayed and deleted later.
        expense = Expense(
            record_id=self.next_id(),
            expense_date=expense_date,
            category=category,
            amount=amount,
            description=description,
        )
        self.expenses.append(expense)
        self.save()
        return expense

    def delete_expense(self, record_id: int) -> bool:
        for index, expense in enumerate(self.expenses):
            if expense.record_id == record_id:
                del self.expenses[index]
                self.save()
                return True
        return False

    def total_spending(self) -> float:
        return sum(expense.amount for expense in self.expenses)

    def spending_by_category(self) -> dict[str, float]:
        totals = {category: 0.0 for category in CATEGORIES}
        for expense in self.expenses:
            totals[expense.category] = totals.get(expense.category, 0.0) + expense.amount
        return totals

    def highest_spending_category(self) -> tuple[str, float] | None:
        totals = self.spending_by_category()
        used_categories = {
            category: amount for category, amount in totals.items() if amount > 0
        }
        if not used_categories:
            return None
        return max(used_categories.items(), key=lambda item: item[1])

    def non_essential_total(self) -> float:
        return sum(
            expense.amount
            for expense in self.expenses
            if expense.category in NON_ESSENTIAL_CATEGORIES
        )

    def calculate_score(self) -> int:
        if not self.expenses:
            return 100

        # The score starts at 100 and changes with the user's spending habits.
        score = 100.0
        total = self.total_spending()
        non_essential = self.non_essential_total()

        # Spending over the target lowers the score; staying under gives a small bonus.
        if self.target_budget is not None and self.target_budget > 0:
            if total > self.target_budget:
                over_ratio = (total - self.target_budget) / self.target_budget
                score -= min(45, over_ratio * 70)
            else:
                under_ratio = (self.target_budget - total) / self.target_budget
                score += min(5, under_ratio * 10)

        # A high optional spending ratio lowers the score.
        if total > 0:
            non_essential_ratio = non_essential / total
            if non_essential_ratio > 0.50:
                score -= 20
            elif non_essential_ratio > 0.35:
                score -= 10
            elif non_essential_ratio <= 0.25:
                score += 5

        # Study expenses receive a small positive reward.
        if any(expense.category == "Study" for expense in self.expenses):
            score += 3

        return max(0, min(100, round(score)))

    def level(self) -> str:
        # Score thresholds decide the game-style user level.
        score = self.calculate_score()
        if score >= 90:
            return "Budget Master"
        if score >= 75:
            return "Smart Spender"
        if score >= 60:
            return "Careful Learner"
        if score >= 40:
            return "Spending Explorer"
        return "Budget Rescue Mode"

    def status(self) -> str:
        # The spending status is a quick summary of the score result.
        score = self.calculate_score()
        if score >= 85:
            return "Safe Zone"
        if score >= 70:
            return "Balanced Zone"
        if score >= 50:
            return "Warning Zone"
        return "Danger Zone"

    def achievements(self) -> list[str]:
        # Achievements are unlocked from the current records and budget result.
        achievements = []
        total = self.total_spending()
        categories_used = {expense.category for expense in self.expenses}
        dates_used = {expense.expense_date for expense in self.expenses}

        if self.expenses:
            achievements.append("First Step - added the first spending record")
        if len(self.expenses) >= 5:
            achievements.append("Record Builder - added five or more records")
        if len(dates_used) >= 3:
            achievements.append("Consistent Tracker - recorded spending on three days")
        if len(categories_used) >= 4:
            achievements.append("Category Explorer - used four or more categories")
        if self.target_budget is not None and total <= self.target_budget:
            achievements.append("Good Saver - stayed within the spending target")
        if total > 0 and self.non_essential_total() / total <= 0.35:
            achievements.append("Smart Balance - kept non-essential spending controlled")
        if any(expense.category == "Study" for expense in self.expenses):
            achievements.append("Study Investor - spent money on learning")

        return achievements

    def feedback(self) -> str:
        if not self.expenses:
            return "Add your first expense to begin the quest."

        total = self.total_spending()
        highest = self.highest_spending_category()

        if self.target_budget is None:
            return "Set a spending target to unlock more accurate budget feedback."

        if total > self.target_budget:
            return "Your total spending is above target. Try reducing optional expenses."

        if highest and highest[0] in NON_ESSENTIAL_CATEGORIES:
            return f"{highest[0]} is your highest spending category. Try to control it next time."

        if self.calculate_score() >= 85:
            return "Great work. Your spending habits are currently well controlled."

        return "You are close to a stronger score. Keep tracking and compare your categories."


def money(amount: float) -> str:
    return f"${amount:.2f}"


def read_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Please enter a value.")


def read_amount(prompt: str) -> float:
    while True:
        value = input(prompt).strip()
        try:
            amount = float(value)
            if amount > 0:
                return amount
            print("Amount must be greater than 0.")
        except ValueError:
            print("Please enter a valid number, for example 12.50.")


def read_target_amount(prompt: str) -> float:
    while True:
        value = input(prompt).strip()
        try:
            amount = float(value)
            if amount >= 0:
                return amount
            print("Target budget cannot be negative.")
        except ValueError:
            print("Please enter a valid number, for example 100.")


def read_date(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if not value:
            return date.today().isoformat()
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Please use the date format YYYY-MM-DD, for example 2026-05-18.")


def choose_category() -> str:
    # Show valid categories before asking the user to choose one.
    print("\nCategories:")
    for index, category in enumerate(CATEGORIES, start=1):
        print(f"{index}. {category}")

    while True:
        choice = input("Choose a category number or name: ").strip()
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(CATEGORIES):
                return CATEGORIES[index - 1]

        formatted = choice.title()
        if formatted in CATEGORIES:
            return formatted

        print("Invalid category. Please choose from the list.")


def add_expense_flow(game: BudgetQuest) -> None:
    print("\n--- Add Expense ---")
    # One expense record needs a date, category, amount, and description.
    expense_date = read_date("Date (YYYY-MM-DD, blank for today): ")
    category = choose_category()
    amount = read_amount("Amount: $")
    description = read_non_empty("Short description: ")

    expense = game.add_expense(expense_date, category, amount, description)
    print(f"\nAdded record #{expense.record_id}.")
    print("Achievement check:")
    print_game_snapshot(game)


def view_records(game: BudgetQuest) -> None:
    print("\n--- Expense Records ---")
    if not game.expenses:
        print("No expenses have been added yet.")
        return

    # Sort by date and ID so the records print in a clear order.
    sorted_expenses = sorted(
        game.expenses, key=lambda expense: (expense.expense_date, expense.record_id)
    )
    print(f"{'ID':<4} {'Date':<12} {'Category':<15} {'Amount':>10} Description")
    print("-" * 65)
    for expense in sorted_expenses:
        print(
            f"{expense.record_id:<4} "
            f"{expense.expense_date:<12} "
            f"{expense.category:<15} "
            f"{money(expense.amount):>10} "
            f"{expense.description}"
        )


def view_summary(game: BudgetQuest) -> None:
    print("\n--- Budget Quest Summary ---")
    if not game.expenses:
        print("No data yet. Add expenses first.")
        return

    totals = game.spending_by_category()
    target = "Not set" if game.target_budget is None else money(game.target_budget)

    print(f"Target Budget: {target}")
    print(f"Total Spending: {money(game.total_spending())}")
    print("\nSpending by Category:")
    for category, amount in totals.items():
        if amount > 0:
            print(f"- {category}: {money(amount)}")

    highest = game.highest_spending_category()
    if highest:
        print(f"\nHighest Spending Category: {highest[0]} ({money(highest[1])})")

    print_game_snapshot(game)
    print(f"Feedback: {game.feedback()}")


def print_game_snapshot(game: BudgetQuest) -> None:
    print(f"Budget Score: {game.calculate_score()}/100")
    print(f"Level: {game.level()}")
    print(f"Spending Status: {game.status()}")


def set_target_budget(game: BudgetQuest) -> None:
    print("\n--- Set Spending Target ---")
    print("This target is used to calculate your Budget Score.")
    print("Enter 0 if you want to remove the current target.")

    # Entering 0 removes the target budget instead of saving a new one.
    amount = read_target_amount("Target budget: $")
    if amount == 0:
        game.target_budget = None
        message = "Target budget removed."
    else:
        game.target_budget = amount
        message = f"Target budget updated to {money(amount)}."
    game.save()
    print(message)


def delete_expense_flow(game: BudgetQuest) -> None:
    print("\n--- Delete Expense ---")
    if not game.expenses:
        print("No expenses to delete.")
        return

    # Show record IDs so the user can choose exactly which record to delete.
    view_records(game)
    while True:
        value = input("Enter the ID to delete, or press Enter to cancel: ").strip()
        if not value:
            print("Delete cancelled.")
            return
        if value.isdigit():
            record_id = int(value)
            if game.delete_expense(record_id):
                print(f"Record #{record_id} deleted.")
                return
            print("No record with that ID was found.")
        else:
            print("Please enter a valid ID number.")


def view_achievements(game: BudgetQuest) -> None:
    print("\n--- Achievements ---")
    achievements = game.achievements()
    if not achievements:
        print("No achievements yet. Add expenses to unlock them.")
        return

    for achievement in achievements:
        print(f"- {achievement}")


def print_menu() -> None:
    print("\n========== Budget Quest ==========")
    print("1. Add expense")
    print("2. View expense records")
    print("3. View summary and game status")
    print("4. Set spending target")
    print("5. Delete expense")
    print("6. View achievements")
    print("7. Save and exit")


def main() -> None:
    game = BudgetQuest()
    # Load previous records before showing the menu.
    game.load()

    print("Welcome to Budget Quest!")
    print("Track spending, improve your score, and level up your money habits.")

    # Keep showing the menu until the user saves and exits.
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()

        # Each menu number calls its matching program operation.
        if choice == "1":
            add_expense_flow(game)
        elif choice == "2":
            view_records(game)
        elif choice == "3":
            view_summary(game)
        elif choice == "4":
            set_target_budget(game)
        elif choice == "5":
            delete_expense_flow(game)
        elif choice == "6":
            view_achievements(game)
        elif choice == "7":
            game.save()
            print("Progress saved. Goodbye!")
            break
        else:
            print("Invalid option. Please choose a number from 1 to 7.")


if __name__ == "__main__":
    main()
