# Scripted Test Cases & Verifications — Northstar One (Aanya)

This document contains 9 comprehensive scripted test conversations covering all mandated edge cases, including opt-out requests, busy customers, and human escalation.

---

## Test Case 1: Normal Inquiry → Successful Booking

### Input Transcript
1. **User**: "Hi, I am looking for a 3 BHK apartment in Sector 79 Gurugram. What is the starting price?"
2. **Bot**: "Hi! Welcome to Northstar One in Sector 79, Gurugram. Our 3 BHK apartments start from ₹1.75 Crore onwards. Are you looking for personal end-use or as an investment?"
3. **User**: "End-use. I'd like to book a site visit on 2026-09-06 at 10:00 AM."
4. **Bot**: "Great! Your site visit for Northstar One is confirmed for 2026-09-06 at 10:00 AM. Someone from our team will call you a day before to coordinate."
5. **User**: "Thank you, that's all!"
6. **Bot**: "Thank you! We look forward to welcoming you on September 6th."

### Expected Behavior
- Bot provides accurate 3 BHK starting price (₹1.75 Crore onwards).
- Backend slot checker verifies `2026-09-06 10:00` availability (`True`).
- Bot confirms booking with clear next steps and ends warmly.

### Resulting Analytics JSON
```json
{
  "customer_name": null,
  "budget_mentioned": null,
  "configuration_interest": "3 BHK",
  "interest_level": "hot",
  "site_visit_status": "booked",
  "follow_up_required": false,
  "objections_raised": [],
  "language_used": "English",
  "conversation_summary": "Customer inquired about 3 BHK starting prices and successfully booked a site visit for 2026-09-06 at 10:00 AM.",
  "do_not_contact": false,
  "escalated_to_human": false,
  "follow_up_preferred_time": null
}
```

---

## Test Case 2: Price Objection Handled → Booking

### Input Transcript
1. **User**: "What is the price for 2 BHK?"
2. **Bot**: "Our 2 BHK apartments at Northstar One start at ₹1.35 Crore onwards."
3. **User**: "₹1.35 Crore seems quite expensive for a 2 BHK."
4. **Bot**: "I understand budget is an important factor. Northstar One offers prime location value in Sector 79 with premium construction by Northstar Homes. Would you like to schedule a quick site visit on 2026-09-07 at 11:00 AM to see the development?"
5. **User**: "Okay, book me for 2026-09-07 11:00."
6. **Bot**: "Your site visit for 2026-09-07 at 11:00 AM has been booked! Our team will reach out prior to your visit."
7. **User**: "Thanks, bye!"
8. **Bot**: "Thank you! Have a wonderful day."

### Expected Behavior
- Bot acknowledges price concern warmly, pivots to location/developer value without discounting.
- Slot `2026-09-07 11:00` is confirmed.

### Resulting Analytics JSON
```json
{
  "customer_name": null,
  "budget_mentioned": "₹1.35 Crore",
  "configuration_interest": "2 BHK",
  "interest_level": "hot",
  "site_visit_status": "booked",
  "follow_up_required": false,
  "objections_raised": [
    "Price seems high for 2 BHK"
  ],
  "language_used": "English",
  "conversation_summary": "Customer raised price objection regarding 2 BHK starting price. Bot highlighted prime Sector 79 value, and customer booked site visit for 2026-09-07 11:00 AM.",
  "do_not_contact": false,
  "escalated_to_human": false,
  "follow_up_preferred_time": null
}
```

---

## Test Case 3: Failed Booking Due to Unavailable Slot → Follow-up Required Flagged

### Input Transcript
1. **User**: "Hi, I want to book a visit on 2026-09-09 at 14:00."
2. **Bot**: "I'm sorry, but that specific slot is not available. Here are the available slots:\n- 2026-09-06 10:00\n- 2026-09-06 16:00\n- 2026-09-07 11:00\n- 2026-09-08 15:00\n- 2026-09-10 10:00\nWould any of these work for you?"
3. **User**: "No, none work for me. Have someone call me later."
4. **Bot**: "Understood! I'll have our sales team call you to arrange a suitable visit time."
5. **User**: "Okay thanks."
6. **Bot**: "Thank you! Have a great day."

### Expected Behavior
- System checks `2026-09-09 14:00` (returns `False`), bot presents exact alternative slots.
- `site_visit_status` set to "failed" and `follow_up_required` set to `true`.

### Resulting Analytics JSON
```json
{
  "customer_name": null,
  "budget_mentioned": null,
  "configuration_interest": null,
  "interest_level": "warm",
  "site_visit_status": "failed",
  "follow_up_required": true,
  "objections_raised": [],
  "language_used": "English",
  "conversation_summary": "Customer requested an unavailable visit slot on 2026-09-09. Declined available alternatives and requested a sales call.",
  "do_not_contact": false,
  "escalated_to_human": false,
  "follow_up_preferred_time": null
}
```

---

## Test Case 4: Hinglish Conversation Handling

### Input Transcript
1. **User**: "Mera naam Vikram hai. Northstar One mein 3BHK starting price kya hai?"
2. **Bot**: "Namaste Vikram ji! Northstar One, Sector 79 Gurugram mein humare 3 BHK apartments ₹1.75 Crore onwards se start hote hain. Kya aap end-use ke liye dekh rahe hain ya investment ke liye?"
3. **User**: "Investment ke liye. Site visit slot book kar do 2026-09-08 ko 15:00 baje."
4. **Bot**: "Aapki site visit 2026-09-08 ko 15:00 baje confirm ho gayi hai! Humari team visit se ek din pehle aapko call karke assist karegi."
5. **User**: "Shukriya, bye."
6. **Bot**: "Aapka bahut bahut dhanyawad Vikram ji! Have a great day!"

### Expected Behavior
- Bot detects Hinglish and responds in fluent natural Hinglish.
- Confirms slot `2026-09-08 15:00`.

### Resulting Analytics JSON
```json
{
  "customer_name": "Vikram",
  "budget_mentioned": null,
  "configuration_interest": "3 BHK",
  "interest_level": "hot",
  "site_visit_status": "booked",
  "follow_up_required": false,
  "objections_raised": [],
  "language_used": "Hinglish",
  "conversation_summary": "Vikram inquired about 3 BHK prices in Hinglish for investment and booked a site visit for 2026-09-08 at 15:00.",
  "do_not_contact": false,
  "escalated_to_human": false,
  "follow_up_preferred_time": null
}
```

---

## Test Case 5: Off-topic / Unknown Info Refusal (No Guessing)

### Input Transcript
1. **User**: "What is the exact possession date and exact square footage of 2BHK?"
2. **Bot**: "I don't have the exact possession date or square footage details on hand right now. I will have our sales team share the complete spec sheet with you directly. May I check if you are interested in a 2 BHK or 3 BHK option?"
3. **User**: "Okay thanks."
4. **Bot**: "Thank you! Our team will reach out with the complete details soon."

### Expected Behavior
- Bot refuses to guess or invent unlisted details (exact sqft / possession date).
- Offers human follow-up.

### Resulting Analytics JSON
```json
{
  "customer_name": null,
  "budget_mentioned": null,
  "configuration_interest": "2 BHK",
  "interest_level": "warm",
  "site_visit_status": "not_requested",
  "follow_up_required": true,
  "objections_raised": [],
  "language_used": "English",
  "conversation_summary": "Customer asked for exact square footage and possession date. Bot refrained from estimating unlisted data and offered sales team follow-up.",
  "do_not_contact": false,
  "escalated_to_human": false,
  "follow_up_preferred_time": null
}
```

---

## Test Case 6: Discount Request Refusal & Follow-up Offer

### Input Transcript
1. **User**: "I like 3 BHK. Can you give me a 10 Lakh discount right now?"
2. **Bot**: "I don't have authorization for custom discounts or price modifications. Our 3 BHK apartments start at ₹1.75 Crore onwards. However, I can pass your request to our sales manager to see what best offers might be available. Would you like to schedule a site visit in the meantime?"
3. **User**: "No, just have someone call me."
4. **Bot**: "Understood! I'll have our sales team reach out to you directly regarding pricing options."

### Expected Behavior
- Refuses to invent discount.
- Flags `follow_up_required: true`.

### Resulting Analytics JSON
```json
{
  "customer_name": null,
  "budget_mentioned": null,
  "configuration_interest": "3 BHK",
  "interest_level": "warm",
  "site_visit_status": "not_requested",
  "follow_up_required": true,
  "objections_raised": [
    "Requested 10 Lakh discount"
  ],
  "language_used": "English",
  "conversation_summary": "Customer requested a ₹10 Lakh discount on 3 BHK. Bot strictly refused custom pricing and passed the request to the sales team.",
  "do_not_contact": false,
  "escalated_to_human": false,
  "follow_up_preferred_time": null
}
```

---

## Test Case 7: Opt-out / Do-Not-Contact Request (Hard Stop)

### Input Transcript
1. **User**: "Please stop contacting me. Remove my number and do not disturb."
2. **Bot**: "Understood completely. I have updated our records and you will not be contacted further. Thank you for your time."

### Expected Behavior
- Bot immediately complies without asking why, trying to sell, or pushing back.
- Closes conversation cleanly.
- Analytics flags `do_not_contact: true`.

### Resulting Analytics JSON
```json
{
  "customer_name": null,
  "budget_mentioned": null,
  "configuration_interest": null,
  "interest_level": "cold",
  "site_visit_status": "not_requested",
  "follow_up_required": false,
  "objections_raised": [],
  "language_used": "English",
  "conversation_summary": "Customer explicitly requested to stop contact. Bot complied immediately and closed the session.",
  "do_not_contact": true,
  "escalated_to_human": false,
  "follow_up_preferred_time": null
}
```

---

## Test Case 8: Busy / Uninterested Customer with Preferred Follow-up Time

### Input Transcript
1. **User**: "Hi, I am quite busy right now in a meeting. Can you contact me later?"
2. **Bot**: "Certainly! What day and time would work best for us to reach out?"
3. **User**: "Call me tomorrow at 4 PM."
4. **Bot**: "Sure, I'll have someone reach out to you tomorrow at 4 PM. Have a productive day!"

### Expected Behavior
- Bot refrains from stacking qualifying questions once customer signals they are busy.
- Captures preferred time ("tomorrow at 4 PM") without continued selling.
- Analytics captures `follow_up_preferred_time: "tomorrow at 4 PM"` and `follow_up_required: true`.

### Resulting Analytics JSON
```json
{
  "customer_name": null,
  "budget_mentioned": null,
  "configuration_interest": null,
  "interest_level": "warm",
  "site_visit_status": "not_requested",
  "follow_up_required": true,
  "objections_raised": [],
  "language_used": "English",
  "conversation_summary": "Customer was busy in a meeting and requested a callback tomorrow at 4 PM. Bot scheduled the follow-up without pushing sales questions.",
  "do_not_contact": false,
  "escalated_to_human": false,
  "follow_up_preferred_time": "tomorrow at 4 PM"
}
```

---

## Test Case 9: Human Escalation (Legal / Loan Query / Manager Request)

### Input Transcript
1. **User**: "I have a legal complaint regarding land clearance and I want to speak to your senior sales manager immediately."
2. **Bot**: "I understand your concern. I am escalating this to our senior sales manager right away. A team member will take over and call you back directly to assist with your query."

### Expected Behavior
- Bot identifies complaint / manager request / out-of-scope legal query and escalates immediately.
- Reassures customer concrete next step.
- Analytics flags `escalated_to_human: true` and `follow_up_required: true`.

### Resulting Analytics JSON
```json
{
  "customer_name": null,
  "budget_mentioned": null,
  "configuration_interest": null,
  "interest_level": "warm",
  "site_visit_status": "not_requested",
  "follow_up_required": true,
  "objections_raised": [
    "Legal land clearance complaint"
  ],
  "language_used": "English",
  "conversation_summary": "Customer raised a legal complaint and requested a senior manager. Bot reassured the customer and escalated the conversation to a human manager.",
  "do_not_contact": false,
  "escalated_to_human": true,
  "follow_up_preferred_time": null
}
```
