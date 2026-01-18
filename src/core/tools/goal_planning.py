"""
Goal Planning Tools

Tools for creating, analyzing, and managing financial goals with prioritization,
trade-off analysis, and risk-adjusted return calculations.
"""

from langchain.tools import tool
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# Session-based goal storage (in-memory)
GOALS_SESSION = {
    "goals": [],
    "current_goal_id": 0
}

# Risk-adjusted expected annual returns
RISK_RETURNS = {
    "low": 0.04,      # 4% (high-grade bonds, savings accounts)
    "medium": 0.07,   # 7% (balanced portfolio)
    "high": 0.10      # 10% (stock-heavy portfolio)
}

# Goal categories for suggestions
GOAL_CATEGORIES = [
    "Emergency Fund",
    "Retirement",
    "Home Down Payment",
    "Education",
    "Vacation",
    "Debt Payoff",
    "Wedding",
    "Car Purchase",
    "Investment",
    "Other"
]


def parse_date(date_str: str) -> date:
    """Parse date string in various formats."""
    formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unable to parse date: {date_str}. Use format YYYY-MM-DD")


def months_between(start: date, end: date) -> int:
    """Calculate number of months between two dates."""
    delta = relativedelta(end, start)
    return delta.years * 12 + delta.months


@tool("create_goal", description="Create a new financial goal with details like name, target amount, target date, current savings, priority, and risk tolerance.")
def create_goal(
    name: str,
    target_amount: float,
    target_date: str,
    current_savings: float = 0.0,
    priority: str = "medium",
    risk_tolerance: str = "medium",
    is_investment_based: bool = False,
    category: str = "Other",
    notes: str = ""
) -> str:
    """
    Create a new financial goal.

    Args:
        name: Name/description of the goal
        target_amount: Target amount to save (in dollars)
        target_date: Target date in YYYY-MM-DD format
        current_savings: Current amount saved toward this goal (default: 0)
        priority: Priority level - 'high', 'medium', or 'low' (default: 'medium')
        risk_tolerance: Risk tolerance - 'low', 'medium', or 'high' (default: 'medium')
        is_investment_based: Whether this goal involves investing (default: False)
        category: Optional category from predefined list (default: 'Other')
        notes: Additional notes about the goal (default: '')

    Returns:
        str: Confirmation message with goal ID and summary
    """
    try:
        # Validate inputs
        if target_amount <= 0:
            return "Error: Target amount must be greater than 0"

        if current_savings < 0:
            return "Error: Current savings cannot be negative"

        if priority.lower() not in ["high", "medium", "low"]:
            return "Error: Priority must be 'high', 'medium', or 'low'"

        if risk_tolerance.lower() not in ["low", "medium", "high"]:
            return "Error: Risk tolerance must be 'low', 'medium', or 'high'"

        # Parse and validate date
        target_date_obj = parse_date(target_date)
        today = date.today()

        if target_date_obj <= today:
            return "Error: Target date must be in the future"

        # Create goal
        GOALS_SESSION["current_goal_id"] += 1
        goal_id = GOALS_SESSION["current_goal_id"]

        goal = {
            "id": goal_id,
            "name": name,
            "target_amount": target_amount,
            "target_date": target_date,
            "current_savings": current_savings,
            "priority": priority.lower(),
            "risk_tolerance": risk_tolerance.lower(),
            "is_investment_based": is_investment_based,
            "category": category,
            "notes": notes,
            "created_at": str(today)
        }

        GOALS_SESSION["goals"].append(goal)

        # Calculate basic stats
        months_left = months_between(today, target_date_obj)
        remaining = target_amount - current_savings

        return (
            f"✓ Goal created successfully!\n\n"
            f"Goal ID: {goal_id}\n"
            f"Name: {name}\n"
            f"Category: {category}\n"
            f"Target: ${target_amount:,.2f}\n"
            f"Current Savings: ${current_savings:,.2f}\n"
            f"Remaining: ${remaining:,.2f}\n"
            f"Target Date: {target_date}\n"
            f"Time Left: {months_left} months\n"
            f"Priority: {priority}\n"
            f"Risk Tolerance: {risk_tolerance}\n"
            f"Investment-Based: {'Yes' if is_investment_based else 'No'}\n"
            f"\nUse 'calculate_savings_required' to see how much you need to save monthly."
        )

    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error creating goal: {str(e)}"


@tool("calculate_savings_required", description="Calculate monthly and annual savings required to reach a financial goal, with or without investment returns.")
def calculate_savings_required(goal_id: int) -> str:
    """
    Calculate savings required to reach a goal.

    Args:
        goal_id: ID of the goal to analyze

    Returns:
        str: Detailed savings calculations including simple and investment-based scenarios
    """
    try:
        # Find goal
        goal = None
        for g in GOALS_SESSION["goals"]:
            if g["id"] == goal_id:
                goal = g
                break

        if not goal:
            return f"Error: Goal with ID {goal_id} not found. Use 'list_goals' to see available goals."

        # Get goal details
        target_amount = goal["target_amount"]
        current_savings = goal["current_savings"]
        target_date_obj = parse_date(goal["target_date"])
        risk_tolerance = goal["risk_tolerance"]
        is_investment = goal["is_investment_based"]

        today = date.today()
        months_left = months_between(today, target_date_obj)
        years_left = months_left / 12.0
        remaining = target_amount - current_savings

        if months_left <= 0:
            return "Error: Target date has passed or is today"

        # Simple calculation (no investment returns)
        monthly_simple = remaining / months_left
        annual_simple = monthly_simple * 12

        result = (
            f"📊 Savings Analysis for: {goal['name']}\n\n"
            f"Target Amount: ${target_amount:,.2f}\n"
            f"Current Savings: ${current_savings:,.2f}\n"
            f"Amount Needed: ${remaining:,.2f}\n"
            f"Time Remaining: {months_left} months ({years_left:.1f} years)\n\n"
            f"--- Simple Savings (No Investment) ---\n"
            f"Monthly Required: ${monthly_simple:,.2f}\n"
            f"Annual Required: ${annual_simple:,.2f}\n\n"
        )

        # Investment-based calculation if applicable
        if is_investment:
            annual_return = RISK_RETURNS[risk_tolerance]
            monthly_return = annual_return / 12

            # Future Value formula for annuity with present value
            # FV = PV(1+r)^n + PMT * [((1+r)^n - 1) / r]
            # Solve for PMT: PMT = (FV - PV(1+r)^n) / [((1+r)^n - 1) / r]

            if monthly_return > 0:
                future_value_of_current = current_savings * ((1 + monthly_return) ** months_left)
                remaining_to_grow = target_amount - future_value_of_current

                # Annuity factor
                annuity_factor = ((1 + monthly_return) ** months_left - 1) / monthly_return

                monthly_investment = remaining_to_grow / annuity_factor if annuity_factor > 0 else remaining / months_left
                annual_investment = monthly_investment * 12

                # Calculate total contributions vs final value
                total_contributions = current_savings + (monthly_investment * months_left)
                investment_gains = target_amount - total_contributions

                result += (
                    f"--- Investment-Based Savings ({risk_tolerance.title()} Risk) ---\n"
                    f"Expected Annual Return: {annual_return * 100:.1f}%\n"
                    f"Monthly Investment Required: ${monthly_investment:,.2f}\n"
                    f"Annual Investment Required: ${annual_investment:,.2f}\n\n"
                    f"Projection:\n"
                    f"  Total You'll Contribute: ${total_contributions:,.2f}\n"
                    f"  Expected Investment Gains: ${investment_gains:,.2f}\n"
                    f"  Final Value: ${target_amount:,.2f}\n\n"
                    f"💡 You save ${monthly_simple - monthly_investment:,.2f}/month by investing!\n"
                )
            else:
                result += "Investment calculation not available (rate too low).\n"
        else:
            result += (
                f"💡 Tip: This is a savings-only goal. Consider setting 'is_investment_based=True' "
                f"if you plan to invest these funds for potentially better returns.\n"
            )

        return result

    except Exception as e:
        return f"Error calculating savings: {str(e)}"


@tool("prioritize_goals", description="Analyze and rank all goals by priority, urgency, and feasibility.")
def prioritize_goals() -> str:
    """
    Analyze and prioritize all goals using a scoring system.

    Returns:
        str: Prioritized list of goals with scores and recommendations
    """
    try:
        if not GOALS_SESSION["goals"]:
            return "No goals found. Create goals first using 'create_goal'."

        today = date.today()
        scored_goals = []

        for goal in GOALS_SESSION["goals"]:
            # Calculate urgency score (0-40 points)
            target_date_obj = parse_date(goal["target_date"])
            months_left = months_between(today, target_date_obj)

            if months_left < 6:
                urgency_score = 40
            elif months_left < 12:
                urgency_score = 30
            elif months_left < 24:
                urgency_score = 20
            else:
                urgency_score = 10

            # Priority score (0-30 points)
            priority_scores = {"high": 30, "medium": 20, "low": 10}
            priority_score = priority_scores[goal["priority"]]

            # Feasibility score (0-30 points)
            remaining = goal["target_amount"] - goal["current_savings"]
            monthly_needed = remaining / months_left if months_left > 0 else remaining

            # Assume reasonable monthly budget of $500 per goal as baseline
            if monthly_needed < 200:
                feasibility_score = 30
            elif monthly_needed < 500:
                feasibility_score = 20
            elif monthly_needed < 1000:
                feasibility_score = 10
            else:
                feasibility_score = 5

            total_score = urgency_score + priority_score + feasibility_score

            scored_goals.append({
                "goal": goal,
                "total_score": total_score,
                "urgency_score": urgency_score,
                "priority_score": priority_score,
                "feasibility_score": feasibility_score,
                "months_left": months_left,
                "monthly_needed": monthly_needed
            })

        # Sort by total score (descending)
        scored_goals.sort(key=lambda x: x["total_score"], reverse=True)

        result = "🎯 Goal Prioritization Analysis\n\n"

        for i, item in enumerate(scored_goals, 1):
            goal = item["goal"]
            result += (
                f"{i}. {goal['name']} (ID: {goal['id']})\n"
                f"   Category: {goal['category']}\n"
                f"   Priority Score: {item['total_score']}/100\n"
                f"   - Urgency: {item['urgency_score']}/40 ({item['months_left']} months left)\n"
                f"   - Importance: {item['priority_score']}/30 ({goal['priority']})\n"
                f"   - Feasibility: {item['feasibility_score']}/30 (${item['monthly_needed']:,.2f}/month needed)\n"
                f"   Target: ${goal['target_amount']:,.2f} by {goal['target_date']}\n\n"
            )

        result += "\n💡 Recommendation: Focus on higher-scoring goals first, but consider your personal priorities too!"

        return result

    except Exception as e:
        return f"Error prioritizing goals: {str(e)}"


@tool("analyze_goal_tradeoffs", description="Analyze trade-offs between competing goals and show resource allocation conflicts.")
def analyze_goal_tradeoffs(monthly_budget: float) -> str:
    """
    Analyze trade-offs between goals given a monthly budget.

    Args:
        monthly_budget: Total monthly budget available for all goals (in dollars)

    Returns:
        str: Trade-off analysis showing budget allocation and conflicts
    """
    try:
        if not GOALS_SESSION["goals"]:
            return "No goals found. Create goals first using 'create_goal'."

        if monthly_budget <= 0:
            return "Error: Monthly budget must be greater than 0"

        today = date.today()
        goal_requirements = []

        # Calculate requirements for each goal
        for goal in GOALS_SESSION["goals"]:
            target_date_obj = parse_date(goal["target_date"])
            months_left = months_between(today, target_date_obj)

            if months_left <= 0:
                continue

            remaining = goal["target_amount"] - goal["current_savings"]

            # Use investment calculation if applicable
            if goal["is_investment_based"]:
                risk = goal["risk_tolerance"]
                monthly_return = RISK_RETURNS[risk] / 12

                if monthly_return > 0:
                    future_value_of_current = goal["current_savings"] * ((1 + monthly_return) ** months_left)
                    remaining_to_grow = goal["target_amount"] - future_value_of_current
                    annuity_factor = ((1 + monthly_return) ** months_left - 1) / monthly_return
                    monthly_needed = remaining_to_grow / annuity_factor if annuity_factor > 0 else remaining / months_left
                else:
                    monthly_needed = remaining / months_left
            else:
                monthly_needed = remaining / months_left

            goal_requirements.append({
                "goal": goal,
                "monthly_needed": monthly_needed,
                "months_left": months_left
            })

        # Sort by priority score
        priority_scores = {"high": 3, "medium": 2, "low": 1}
        goal_requirements.sort(
            key=lambda x: (priority_scores[x["goal"]["priority"]], -x["months_left"]),
            reverse=True
        )

        # Calculate total requirements
        total_needed = sum(item["monthly_needed"] for item in goal_requirements)
        budget_deficit = total_needed - monthly_budget

        result = f"💰 Trade-Off Analysis\n\n"
        result += f"Monthly Budget Available: ${monthly_budget:,.2f}\n"
        result += f"Total Monthly Needed: ${total_needed:,.2f}\n"

        if budget_deficit > 0:
            result += f"⚠️  Budget Shortfall: ${budget_deficit:,.2f}/month\n\n"
        else:
            result += f"✓ Budget Surplus: ${abs(budget_deficit):,.2f}/month\n\n"

        result += "Goal Requirements:\n"

        running_allocation = 0
        for i, item in enumerate(goal_requirements, 1):
            goal = item["goal"]
            monthly_needed = item["monthly_needed"]
            running_allocation += monthly_needed

            # Determine status
            if running_allocation <= monthly_budget:
                status = "✓ Fully Fundable"
                allocated = monthly_needed
            elif running_allocation - monthly_needed < monthly_budget:
                allocated = monthly_budget - (running_allocation - monthly_needed)
                status = f"⚠️  Partially Fundable (${allocated:,.2f})"
            else:
                allocated = 0
                status = "✗ Not Fundable"

            result += (
                f"\n{i}. {goal['name']} ({goal['priority'].upper()} priority)\n"
                f"   Needs: ${monthly_needed:,.2f}/month\n"
                f"   Status: {status}\n"
                f"   Target: ${goal['target_amount']:,.2f} by {goal['target_date']}\n"
            )

        # Provide recommendations
        result += "\n\n📌 Recommendations:\n"

        if budget_deficit > 0:
            result += (
                f"• You need an additional ${budget_deficit:,.2f}/month to fund all goals\n"
                f"• Consider:\n"
                f"  - Extending timelines for lower-priority goals\n"
                f"  - Reducing target amounts for less critical goals\n"
                f"  - Increasing income or reducing expenses by ${budget_deficit:,.2f}/month\n"
                f"  - Focusing on top {sum(1 for item in goal_requirements if (sum(x['monthly_needed'] for x in goal_requirements[:goal_requirements.index(item)+1])) <= monthly_budget)} goal(s) first\n"
            )
        else:
            result += (
                f"• Good news! You can fund all goals with your current budget\n"
                f"• Consider using the ${abs(budget_deficit):,.2f}/month surplus to:\n"
                f"  - Reach goals faster\n"
                f"  - Add a new goal\n"
                f"  - Build additional emergency savings\n"
            )

        return result

    except Exception as e:
        return f"Error analyzing trade-offs: {str(e)}"


@tool("check_goal_feasibility", description="Check if a specific goal is realistic and achievable given constraints.")
def check_goal_feasibility(goal_id: int, monthly_budget: float) -> str:
    """
    Check if a goal is feasible given budget constraints.

    Args:
        goal_id: ID of the goal to check
        monthly_budget: Monthly budget available for this goal (in dollars)

    Returns:
        str: Feasibility analysis with recommendations
    """
    try:
        # Find goal
        goal = None
        for g in GOALS_SESSION["goals"]:
            if g["id"] == goal_id:
                goal = g
                break

        if not goal:
            return f"Error: Goal with ID {goal_id} not found"

        if monthly_budget <= 0:
            return "Error: Monthly budget must be greater than 0"

        today = date.today()
        target_date_obj = parse_date(goal["target_date"])
        months_left = months_between(today, target_date_obj)

        if months_left <= 0:
            return "Error: Target date has passed"

        remaining = goal["target_amount"] - goal["current_savings"]

        # Calculate required monthly amount
        if goal["is_investment_based"]:
            risk = goal["risk_tolerance"]
            monthly_return = RISK_RETURNS[risk] / 12

            if monthly_return > 0:
                future_value_of_current = goal["current_savings"] * ((1 + monthly_return) ** months_left)
                remaining_to_grow = goal["target_amount"] - future_value_of_current
                annuity_factor = ((1 + monthly_return) ** months_left - 1) / monthly_return
                monthly_required = remaining_to_grow / annuity_factor if annuity_factor > 0 else remaining / months_left
            else:
                monthly_required = remaining / months_left
        else:
            monthly_required = remaining / months_left

        result = f"🔍 Feasibility Check: {goal['name']}\n\n"
        result += f"Target: ${goal['target_amount']:,.2f} by {goal['target_date']}\n"
        result += f"Current Savings: ${goal['current_savings']:,.2f}\n"
        result += f"Remaining: ${remaining:,.2f}\n"
        result += f"Time Left: {months_left} months\n\n"
        result += f"Monthly Required: ${monthly_required:,.2f}\n"
        result += f"Your Monthly Budget: ${monthly_budget:,.2f}\n\n"

        # Determine feasibility
        if monthly_required <= monthly_budget:
            surplus = monthly_budget - monthly_required
            result += f"✓ FEASIBLE!\n\n"
            result += f"You have a surplus of ${surplus:,.2f}/month\n\n"
            result += "Options:\n"
            result += f"• Stay on current timeline and save the surplus\n"
            result += f"• Accelerate by {int((remaining / monthly_budget))} months to reach goal sooner\n"
            result += f"• Use surplus for another goal\n"
        else:
            deficit = monthly_required - monthly_budget
            result += f"⚠️  CHALLENGING\n\n"
            result += f"Budget shortfall: ${deficit:,.2f}/month\n\n"
            result += "Options to make it feasible:\n"

            # Option 1: Extend timeline
            new_months = int(remaining / monthly_budget) + 1
            new_date = today + relativedelta(months=new_months)
            result += f"1. Extend timeline to {new_date.strftime('%Y-%m-%d')} ({new_months} months)\n"

            # Option 2: Reduce target
            achievable_target = goal["current_savings"] + (monthly_budget * months_left)
            if goal["is_investment_based"] and monthly_return > 0:
                # Adjust for investment returns
                fv_current = goal["current_savings"] * ((1 + monthly_return) ** months_left)
                annuity_future = monthly_budget * (((1 + monthly_return) ** months_left - 1) / monthly_return)
                achievable_target = fv_current + annuity_future

            result += f"2. Reduce target to ${achievable_target:,.2f} (achievable with current budget)\n"

            # Option 3: Increase budget
            result += f"3. Increase monthly budget by ${deficit:,.2f} to ${monthly_required:,.2f}\n"

            # Option 4: Add more to current savings
            needed_upfront = deficit * months_left
            result += f"4. Add ${needed_upfront:,.2f} to current savings now\n"

        return result

    except Exception as e:
        return f"Error checking feasibility: {str(e)}"


@tool("list_goals", description="List all current financial goals with their basic details.")
def list_goals() -> str:
    """
    List all goals currently in the session.

    Returns:
        str: Formatted list of all goals
    """
    try:
        if not GOALS_SESSION["goals"]:
            return "No goals found. Create your first goal using 'create_goal'."

        result = f"📋 Your Financial Goals ({len(GOALS_SESSION['goals'])} total)\n\n"

        for goal in GOALS_SESSION["goals"]:
            today = date.today()
            target_date_obj = parse_date(goal["target_date"])
            months_left = months_between(today, target_date_obj)
            remaining = goal["target_amount"] - goal["current_savings"]
            progress = (goal["current_savings"] / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0

            result += (
                f"ID {goal['id']}: {goal['name']}\n"
                f"  Category: {goal['category']}\n"
                f"  Target: ${goal['target_amount']:,.2f} by {goal['target_date']}\n"
                f"  Progress: ${goal['current_savings']:,.2f} ({progress:.1f}%) - ${remaining:,.2f} remaining\n"
                f"  Time Left: {months_left} months\n"
                f"  Priority: {goal['priority'].title()} | Risk: {goal['risk_tolerance'].title()}\n"
                f"  Investment-Based: {'Yes' if goal['is_investment_based'] else 'No'}\n"
            )

            if goal["notes"]:
                result += f"  Notes: {goal['notes']}\n"

            result += "\n"

        return result

    except Exception as e:
        return f"Error listing goals: {str(e)}"


@tool("update_goal_progress", description="Update the current savings amount for a goal to track progress.")
def update_goal_progress(goal_id: int, new_current_savings: float) -> str:
    """
    Update current savings for a goal.

    Args:
        goal_id: ID of the goal to update
        new_current_savings: New current savings amount

    Returns:
        str: Confirmation message with updated progress
    """
    try:
        # Find goal
        goal = None
        for g in GOALS_SESSION["goals"]:
            if g["id"] == goal_id:
                goal = g
                break

        if not goal:
            return f"Error: Goal with ID {goal_id} not found"

        if new_current_savings < 0:
            return "Error: Current savings cannot be negative"

        old_savings = goal["current_savings"]
        goal["current_savings"] = new_current_savings

        progress = (new_current_savings / goal["target_amount"] * 100) if goal["target_amount"] > 0 else 0
        remaining = goal["target_amount"] - new_current_savings
        change = new_current_savings - old_savings

        result = f"✓ Updated progress for: {goal['name']}\n\n"
        result += f"Previous: ${old_savings:,.2f}\n"
        result += f"Current: ${new_current_savings:,.2f}\n"
        result += f"Change: ${change:+,.2f}\n\n"
        result += f"Progress: {progress:.1f}% complete\n"
        result += f"Remaining: ${remaining:,.2f}\n"

        if remaining <= 0:
            result += f"\n🎉 Congratulations! You've reached your goal!\n"

        return result

    except Exception as e:
        return f"Error updating progress: {str(e)}"


@tool("delete_goal", description="Delete a goal from the current session.")
def delete_goal(goal_id: int) -> str:
    """
    Delete a goal.

    Args:
        goal_id: ID of the goal to delete

    Returns:
        str: Confirmation message
    """
    try:
        # Find and remove goal
        goal_index = None
        for i, g in enumerate(GOALS_SESSION["goals"]):
            if g["id"] == goal_id:
                goal_index = i
                break

        if goal_index is None:
            return f"Error: Goal with ID {goal_id} not found"

        deleted_goal = GOALS_SESSION["goals"].pop(goal_index)

        return f"✓ Deleted goal: {deleted_goal['name']} (ID: {goal_id})"

    except Exception as e:
        return f"Error deleting goal: {str(e)}"


@tool("get_goal_categories", description="Get list of suggested goal categories to help organize goals.")
def get_goal_categories() -> str:
    """
    Get list of suggested goal categories.

    Returns:
        str: List of available categories
    """
    result = "📁 Suggested Goal Categories:\n\n"
    for i, category in enumerate(GOAL_CATEGORIES, 1):
        result += f"{i}. {category}\n"

    result += "\nYou can use these when creating goals, or create your own custom category."

    return result
