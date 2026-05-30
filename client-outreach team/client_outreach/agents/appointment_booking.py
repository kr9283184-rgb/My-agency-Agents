from typing import Optional
from datetime import datetime, timedelta
from client_outreach.agents.base_agent import BaseAgent
from client_outreach.calendar.caldav_calendar import CalDAVCalendar


class AppointmentBookingAgent(BaseAgent):
    def __init__(self, calendar: Optional[CalDAVCalendar] = None, **kwargs):
        super().__init__(**kwargs)
        self.calendar = calendar or CalDAVCalendar()

    def suggest_slots(self, lead_id: str, num_slots: int = 3) -> list[str]:
        lead = self.db.get_lead(lead_id)
        if not lead:
            self.log(f"Lead {lead_id} not found")
            return []

        now = datetime.now()
        slots = []
        for i in range(num_slots):
            day_offset = 1 + i
            slot = now + timedelta(days=day_offset)
            slot = slot.replace(hour=10, minute=0, second=0, microsecond=0)
            slots.append(slot.isoformat())

        slot_strs = [datetime.fromisoformat(s).strftime("%A, %B %d at %I:%M %p") for s in slots]
        self.log(f"Suggested slots for {lead.get('company_name', lead_id)}: {slot_strs}")
        return slot_strs

    def propose_slots(self, lead: dict) -> Optional[int]:
        lead_id = lead.get("lead_id", "")
        slots = self.suggest_slots(lead_id)
        slot_str = "; ".join(slots)

        self.db.add_appointment({
            "lead_id": lead_id,
            "title": f"Sales Meeting — {lead.get('company_name', '')}",
            "description": f"Proposed slots: {slot_str}",
            "proposed_slot": slot_str,
            "status": "pending",
        })

        self.log(f"Proposed meeting slots to {lead.get('company_name', lead_id)}")
        return self.db._get_conn().execute(
            "SELECT MAX(appointment_id) FROM appointments"
        ).fetchone()[0]

    def confirm_appointment(self, appointment_id: int, confirmed_slot: str) -> bool:
        conn = self.db._get_conn()
        try:
            apt = conn.execute(
                "SELECT * FROM appointments WHERE appointment_id = ?",
                (appointment_id,),
            ).fetchone()
            if not apt:
                return False

            conn.execute(
                "UPDATE appointments SET status = 'confirmed', confirmed_slot = ? WHERE appointment_id = ?",
                (confirmed_slot, appointment_id),
            )
            conn.commit()

            lead_id = apt["lead_id"]
            self.db.update_pipeline_stage(lead_id, "Meeting Booked")

            event_id = self.calendar.create_event(
                summary=apt["title"],
                description=apt["description"],
                start_dt=confirmed_slot,
            )
            if event_id:
                conn.execute(
                    "UPDATE appointments SET calendar_event_id = ? WHERE appointment_id = ?",
                    (event_id, appointment_id),
                )
                conn.commit()

            self.log(f"Confirmed appointment {appointment_id} at {confirmed_slot}")
            return True
        finally:
            conn.close()

    def cancel_appointment(self, appointment_id: int) -> bool:
        conn = self.db._get_conn()
        try:
            apt = conn.execute(
                "SELECT * FROM appointments WHERE appointment_id = ?",
                (appointment_id,),
            ).fetchone()
            if not apt:
                return False

            if apt["calendar_event_id"]:
                self.calendar.delete_event(apt["calendar_event_id"])

            conn.execute(
                "UPDATE appointments SET status = 'cancelled' WHERE appointment_id = ?",
                (appointment_id,),
            )
            conn.commit()
            self.log(f"Cancelled appointment {appointment_id}")
            return True
        finally:
            conn.close()

    def send_reminders(self) -> int:
        conn = self.db._get_conn()
        try:
            upcoming = conn.execute("""
                SELECT a.*, l.company_name, l.contact_name, l.whatsapp_phone, l.email
                FROM appointments a
                JOIN leads l ON a.lead_id = l.lead_id
                WHERE a.status = 'confirmed'
                  AND a.reminder_sent = 0
                  AND a.confirmed_slot <= datetime('now', '+1 day')
                  AND a.confirmed_slot > datetime('now')
            """).fetchall()

            count = 0
            for apt in upcoming:
                slot = apt["confirmed_slot"]
                try:
                    dt = datetime.fromisoformat(slot)
                    formatted = dt.strftime("%A, %B %d at %I:%M %p")
                except (ValueError, TypeError):
                    formatted = slot

                if apt["whatsapp_phone"]:
                    self.log(f"[SIMULATED] WhatsApp reminder to {apt['whatsapp_phone']}: "
                             f"Reminder: Meeting with {apt.get('company_name', '')} on {formatted}")

                if apt["email"]:
                    self.log(f"[SIMULATED] Email reminder to {apt['email']}: "
                             f"Reminder: Meeting on {formatted}")

                conn.execute(
                    "UPDATE appointments SET reminder_sent = 1 WHERE appointment_id = ?",
                    (apt["appointment_id"],),
                )
                conn.commit()
                count += 1

            self.log(f"Sent {count} appointment reminders")
            return count
        finally:
            conn.close()
