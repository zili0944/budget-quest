Budget Quest - Gamified Budget Tracker

How to run:
1. Open a terminal in this folder.
2. Run:
   python3 budget_quest.py
3. If your computer uses python instead of python3, run:
   python budget_quest.py

Main file:
budget_quest.py

Data file:
budget_records.json is created automatically when the program saves data. It
does not need to be submitted.

Project description:
Budget Quest is a Python command-line program that helps students record and
analyse their spending habits. Users can add expenses, view saved records, set a
spending target, delete records, and view a spending summary. The program also
includes simple gamified features such as a Budget Score, spending level,
spending status, feedback, and achievements. This makes a normal budget tracker
more engaging while keeping the program realistic and easy to use.

Target audience:
The target audience is students who want a simple tool to track daily spending
and build better money habits.

Key features:
- Add expense records with date, category, amount, and description.
- View all saved records in a clear command-line table.
- Set a personal spending target.
- Calculate total spending and spending by category.
- Show the highest spending category.
- Calculate a Budget Score out of 100.
- Assign a level such as Budget Master or Smart Spender.
- Show spending status such as Safe Zone, Warning Zone, or Danger Zone.
- Unlock simple achievements.
- Save and load data using a JSON file.

Advanced programming concepts used:
1. Object-oriented programming:
   The program uses an Expense class and a BudgetQuest class to organise data
   and behaviour.

2. File handling and JSON:
   Spending records and the target budget are saved to budget_records.json and
   loaded again when the program starts.

Additional concepts:
- Lists and dictionaries for storing and summarising records.
- Dataclasses for structured expense data.
- Date validation using datetime.
- Input validation and error handling.
- Sorting records by date.
- Conditional logic for score, level, status, feedback, and achievements.

