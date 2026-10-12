"""Import 30 fictional leadership reflections into an existing Reflect account.
Usage: stop the Reflect server, place this file beside server.py, run python add_30_reflections.py.
No dependencies; will not alter existing reflections or credentials.
"""
import sqlite3
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

DB = Path(__file__).resolve().parent / 'reflect.sqlite3'
ENTRIES = [
('Two teammates were unsure who owned the client handoff, and the deliverable was delayed.','I clarified the owner in a short team message, but only after the confusion surfaced.','State a single owner and handoff criteria at the start of shared projects.'),
('During the Monday team meeting, we spent fifteen minutes discussing updates already in chat.','I shortened the discussion and asked everyone to post blockers instead.','Meetings should focus on decisions and obstacles rather than repeating status.'),
('A designer received urgent revisions while finishing a scheduled launch task.','I told them to handle both requests without explicitly changing the priority.','When new work arrives, I need to name what can move or wait.'),
('A new teammate asked three different people how to submit a final draft.','I documented the process and assigned one person to answer workflow questions.','Clear onboarding and ownership can prevent repeated uncertainty.'),
('I hesitated to give direct feedback on an incomplete report.','I rewrote portions myself because the deadline was close.','Avoiding feedback may solve the immediate problem but reduce learning.'),
('A client praised how quickly our team resolved an unexpected issue.','I thanked the individuals publicly and described their specific contributions.','Specific recognition is more meaningful than a generic compliment.'),
('Our daily stand-up ran long because we debated a technical detail with the whole group.','I moved the discussion into a smaller follow-up meeting.','A focused agenda helps protect the team’s time.'),
('A content task was marked complete, but nobody knew who approved the final version.','I asked the team to define the reviewer and update the workflow board.','Finishing work requires clarity about both execution and approval.'),
('Two stakeholders requested different changes to the same campaign.','I asked for a single prioritized brief before directing the team.','Conflicting priorities need resolution before work is assigned.'),
('One teammate appeared quiet in our planning session despite having relevant expertise.','I checked in privately and invited their perspective without putting them on the spot.','I should create multiple ways for team members to contribute.'),
('The team missed a minor milestone because feedback arrived later than expected.','I updated the timeline but did not clarify the feedback owner early enough.','A deadline is only realistic when review responsibilities are explicit.'),
('A teammate seemed discouraged after receiving vague comments on a draft.','I scheduled a short one-on-one and gave two concrete examples of what to change.','Actionable feedback is easier to apply than general criticism.'),
('We started a meeting with no decision to make and still used the full half hour.','I ended early and shared a concise written update afterward.','Question whether a meeting is necessary before scheduling it.'),
('An urgent request arrived while three team members were at capacity.','I negotiated a later deadline and explained which work would be postponed.','Protecting focus can require communicating trade-offs openly.'),
('A junior teammate completed a difficult customer response independently.','I recognized the effort and asked what support had helped them succeed.','Good leadership includes noticing growth, not just correcting mistakes.'),
('A handoff between marketing and development left a page unpublished for a day.','I mapped the steps and added an explicit publishing owner.','Cross-functional handoffs need visible responsibilities.'),
('A team member asked for clearer expectations after I said a design needed to feel more polished.','I provided examples and objective acceptance criteria.','Feedback should describe observable changes rather than personal taste.'),
('Our weekly planning meeting ended with several tasks but no confirmed due dates.','I followed up in writing to assign owners and dates.','Close meetings by recording ownership, deadlines and next steps.'),
('A stakeholder requested a new feature halfway through a sprint.','I asked the team to estimate its impact before agreeing to the change.','A request can be valuable without automatically becoming the top priority.'),
('Two colleagues disagreed over who should contact a customer.','I facilitated a brief discussion and documented the final responsibility.','Resolving ownership together is better than making assumptions.'),
('A teammate shared that previous feedback felt surprising at review time.','I committed to shorter and more frequent check-ins.','Feedback should be timely enough to support improvement.'),
('Our retro surfaced frustration with recurring status meetings.','I asked the team to vote on which updates could be asynchronous.','Meeting routines should evolve based on team needs.'),
('A project entered the final stage without enough time for quality checks.','I moved a nonessential request to the next cycle and protected the review window.','Priorities should include time for quality assurance.'),
('A customer complimented the helpfulness of a support teammate.','I shared the feedback with the team and added it to our weekly wins.','Recognition can strengthen morale when it is timely and specific.'),
('A last-minute revision exposed uncertainty around the final approver.','I identified one decision-maker and shared the updated workflow.','Repeated handoff confusion is worth addressing at the process level.'),
('I noticed I was talking more than others during our planning meeting.','I asked each teammate for their view and left time for questions.','Space for quieter perspectives improves collective judgment.'),
('I delayed discussing a repeated formatting issue with a teammate.','I finally used an example and offered a reusable checklist.','Early supportive feedback can avoid repeated rework.'),
('Two deliverables slipped because an urgent request displaced planned work.','I reviewed priorities with the requester and reset expectations openly.','Visible trade-offs help the team understand why timelines change.'),
('Our weekly sync ended early after we shared the agenda and decisions in advance.','I maintained a short live discussion for unresolved blockers only.','Structured, purposeful meetings can preserve focus.'),
('At the end of the month, I reviewed several cases of unclear task ownership.','I proposed a shared assignment template with an owner, reviewer and due date.','I should test whether clearer handoff rules actually reduce delays.')]


def main():
    if not DB.exists():
        raise SystemExit(f'Database not found: {DB}\nPlace this file in the SAME folder as server.py and reflect.sqlite3.')
    db = sqlite3.connect(str(DB), timeout=10)
    db.row_factory = sqlite3.Row
    try:
        users = db.execute('SELECT id, name, email FROM users ORDER BY id').fetchall()
        if not users:
            raise SystemExit('No Reflect accounts found. Create/sign into your account first.')
        print('\nAccounts found in your existing Reflect database:')
        for u in users:
            print(f'  {u["id"]}: {u["name"]} <{u["email"]}>')
        selected = input('\nEnter the account ID to receive 30 fictional entries (or press Enter to cancel): ').strip()
        if not selected or not selected.isdigit() or int(selected) not in {u['id'] for u in users}:
            raise SystemExit('Cancelled. No changes made.')
        user_id = int(selected)
        existing = db.execute("SELECT COUNT(*) FROM reflections WHERE user_id=? AND situation LIKE '[Demo %/30] %'", (user_id,)).fetchone()[0]
        if existing:
            raise SystemExit(f'This account already has {existing} demo entries. Nothing imported; duplicates avoided.')
        backup = DB.with_name('reflect_before_demo.sqlite3')
        if backup.exists():
            backup = DB.with_name(f'reflect_before_demo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sqlite3')
        with sqlite3.connect(str(backup)) as target:
            db.backup(target)
        today = date.today()
        created = datetime.now(timezone.utc).isoformat(timespec='seconds')
        with db:
            for n, (situation, response, learning) in enumerate(ENTRIES, 1):
                happened = (today - timedelta(days=30-n)).isoformat()
                db.execute('INSERT INTO reflections (user_id,situation,response,learning,happened_on,created_at) VALUES (?,?,?,?,?,?)',
                           (user_id, f'[Demo {n:02d}/30] {situation}',response,learning,happened,created))
        print(f'\nDone! Imported {len(ENTRIES)} fictional reflections into account ID {user_id}.')
        print(f'Database backup saved: {backup.name}')
        print('Start Reflect, refresh the page, then open Reflection History or Insights & Patterns.')
        print('Reminder: These are fictional demo entries, not your personal reflections.')
    finally:
        db.close()

if __name__ == '__main__':
    main()
