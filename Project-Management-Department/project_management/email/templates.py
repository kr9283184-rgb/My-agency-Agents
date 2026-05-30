WEEKLY_UPDATE_TEMPLATE = """Subject: Weekly Project Update — {company} ({completion_pct:.0f}% Complete)

Hi {contact_name},

Here is your weekly update for {company}.

Overall Progress: {completion_pct:.0f}%
Tasks Completed: {completed}/{total}

Current Milestones:
{milestones_text}

{risks_text}
Next Steps:
- Continue with current development activities
- Prepare for upcoming milestones
- We will be in touch with any updates

Best regards,
Project Management Team
"""

MILESTONE_COMPLETE_TEMPLATE = """Subject: Milestone Completed: {milestone_title} — {company}

Hi {contact_name},

We are pleased to inform you that the milestone '{milestone_title}' has been completed successfully.

What was delivered:
{deliverables}

Next Steps:
The project is moving to the next phase. We'll keep you updated on progress.

Best regards,
Project Management Team
"""

DELIVERY_NOTIFICATION_TEMPLATE = """Subject: Project Delivered — {company}

Hi {contact_name},

We are excited to inform you that your project has been completed and delivered!

What was delivered:
- All project requirements have been met
- QA testing has been passed
- Documentation has been prepared

Next Steps:
1. Review the delivered project
2. Provide final feedback within 7 days
3. Schedule a closeout meeting if needed

Thank you for choosing us!

Best regards,
Project Management Team
"""

DELAY_NOTIFICATION_TEMPLATE = """Subject: Project Update: Schedule Adjustment — {company}

Hi {contact_name},

We want to keep you informed about a schedule adjustment for your project.

Issue: {issue}
Impact: {impact}
New Timeline: {new_timeline}

Our Response:
{mitigation}

We apologize for any inconvenience and appreciate your understanding.

Best regards,
Project Management Team
"""
