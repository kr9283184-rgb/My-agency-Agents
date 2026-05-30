import os
from typing import Optional
from onboarding_department.agents.base_agent import BaseAgent


class ContractAgent(BaseAgent):
    def verify_contract(self, lead: dict, proposal: Optional[dict] = None, output_dir: str = "") -> dict:
        lead_id = lead.get("lead_id", "")
        company = lead.get("company_name", "")

        proposal_data = proposal or self.db.get_proposal_from_outreach(lead_id)

        agreement_signed = bool(proposal_data and proposal_data.get("status") == "accepted")
        payment_status = "pending"
        invoice_status = "pending"
        remaining_balance = 0.0

        if proposal_data:
            payment_status = "confirmed" if agreement_signed else "pending"
            invoice_status = "sent" if proposal_data.get("sent_at") else "pending"
            remaining_balance = float(proposal_data.get("amount", 0))

        if agreement_signed and remaining_balance > 0:
            payment_status = "partial"
            invoice_status = "sent"

        details = {
            "company": company,
            "agreement_signed": agreement_signed,
            "proposal_id": (proposal_data or {}).get("proposal_id", ""),
            "proposal_type": (proposal_data or {}).get("proposal_type", ""),
            "deal_amount": (proposal_data or {}).get("amount", 0),
            "payment_status": payment_status,
            "invoice_status": invoice_status,
            "remaining_balance": remaining_balance,
            "proposal_sent_at": (proposal_data or {}).get("sent_at", ""),
        }

        file_path = ""
        if output_dir:
            company_dir = os.path.join(output_dir, company.replace(" ", "_"))
            os.makedirs(company_dir, exist_ok=True)
            file_path = os.path.join(company_dir, "08_contract_verification.md")
            with open(file_path, "w") as f:
                self._write_report(f, details)

        self.log(f"Contract verified for {company}: signed={agreement_signed}, payment={payment_status}")

        return {"file_path": file_path, "details": details}

    def _write_report(self, f, details: dict):
        f.write(f"# Contract & Payment Verification — {details.get('company', '')}\n\n")
        f.write("---\n\n")

        f.write("## Agreement Status\n\n")
        signed = details.get("agreement_signed", False)
        f.write(f"- **Agreement Signed:** {'Yes' if signed else 'No'}\n")
        f.write(f"- **Proposal ID:** {details.get('proposal_id', 'N/A')}\n")
        f.write(f"- **Proposal Type:** {details.get('proposal_type', 'N/A')}\n")
        f.write(f"- **Proposal Sent:** {details.get('proposal_sent_at', 'N/A')}\n\n")

        f.write("## Payment Status\n\n")
        f.write(f"- **Deal Amount:** ${float(details.get('deal_amount', 0)):,.2f}\n")
        f.write(f"- **Payment Status:** {details.get('payment_status', 'pending').title()}\n")
        f.write(f"- **Invoice Status:** {details.get('invoice_status', 'pending').title()}\n")
        f.write(f"- **Remaining Balance:** ${float(details.get('remaining_balance', 0)):,.2f}\n\n")

        f.write("## Summary\n\n")
        if signed:
            f.write("All contractual requirements have been met. The project is ready to proceed.\n")
        else:
            f.write("Awaiting agreement signature and payment confirmation.\n")

        f.write("\n---\n")
        f.write("*This document was automatically generated during onboarding.*\n")
