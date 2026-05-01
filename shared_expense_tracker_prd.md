# Product Requirements Document (PRD)

## Project Title
**Shared Expense Tracking and Payment Verification System**

---

## 1. Overview

The Shared Expense Tracking and Payment Verification System is a web-based application designed to help groups manage shared expenses in a transparent, organized, and user-friendly way.

This system is mainly useful for friends, roommates, classmates, teammates, or any group of people who regularly share expenses. It helps users track who paid, how much each person owes, payment status, and proof of payment.

---

## 2. Problem Statement

Managing shared expenses manually can be confusing and time-consuming. People often forget who paid, how much each person owes, whether a payment was settled, and whether the receiver actually received the payment.

Common problems include:

- Miscommunication between group members
- Manual calculation errors
- Difficulty tracking pending payments
- Lack of proof for completed payments
- No clear history of past expenses
- Confusion in group-wise expense management

This system aims to solve these problems by providing a centralized platform for shared expense tracking and payment verification.

---

## 3. Goal of the Product

The main goal of this application is to simplify shared expense management by allowing users to record expenses, calculate balances automatically, track payment status, upload payment proof, and confirm received payments.

The system should improve:

- Accuracy
- Transparency
- Trust between users
- Ease of expense management
- Payment tracking efficiency

---

## 4. Target Users

The target users of this system include:

- Students
- Roommates
- Friends
- Project teammates
- Travel groups
- Small event groups
- Shared household members

---

## 5. Key Features

## 5.1 User Registration and Login

Users should be able to create an account and securely log in to the system.

### Requirements

- User can register with basic details.
- User can log in using valid credentials.
- Each user should have their own personal dashboard.
- Users should only access expenses and groups they are part of.

---

## 5.2 Personal Dashboard

After logging in, users should be directed to their own dashboard.

### Dashboard Should Display

- Expense groups the user belongs to
- Pending payments
- Completed payments
- Payment requests
- Monthly expense summary
- Recent activity
- Notifications

---

## 5.3 Expense Groups

Users should be able to create and manage expense groups.

### Examples

- Roommates
- Trip group
- Classmates
- Team lunch
- Event group

### Requirements

- User can create an expense group.
- User can add other registered users to the group.
- Group members can view shared expenses.
- Only group members can participate in group expenses.

---

## 5.4 Add Members to Expenses

Similar to a collaborative board concept, users can be added to specific groups or individual expense records.

### Requirements

- A user can add participants to an expense.
- Only selected participants are included in the split calculation.
- Each participant can view their own payable amount.
- Participants can track their payment status.

---

## 5.5 Add Expense

Users should be able to record a new shared expense.

### Expense Details

- Expense title
- Amount
- Paid by
- Date
- Category
- Participants
- Description or note

### Requirements

- The system should allow users to enter expense details.
- The system should calculate each participant’s share.
- The expense should be visible to all selected participants.
- The payer should be clearly shown.

---

## 5.6 Expense Categories

Expenses should be organized using categories.

### Example Categories

- Food
- Rent
- Travel
- Utilities
- Shopping
- Events
- Other

### Requirements

- User can select a category while adding an expense.
- Expenses can be filtered by category.
- Category-based summaries can be generated.

---

## 5.7 Automatic Split Calculation

The system should automatically calculate how much each participant owes.

### Requirements

- Equal split calculation should be supported.
- The system should display individual payable amounts.
- The total split amount should match the original expense amount.
- Future improvement can include custom split amounts.

---

## 5.8 Payment Status Tracking

Each participant should have a payment status for every expense.

### Payment Status Types

- Pending
- Paid
- Verified

### Requirements

- Users can mark their payment as paid.
- The payment status should update clearly.
- The payer or receiver can verify the payment.
- Users should be able to view pending and completed payments separately.

---

## 5.9 Payment Proof Upload

Users should be able to upload proof after settling payment.

### Accepted Proof Types

- JPG image
- PNG image
- PDF receipt

### Requirements

- User can upload payment proof.
- Proof should be attached to the related payment.
- Other relevant group members should be able to view the proof.
- The proof helps improve trust and transparency.

---

## 5.10 Payment Confirmation

The person who receives the payment should be able to confirm whether the payment was actually received.

### Requirements

- Receiver can approve or reject payment proof.
- Once approved, payment status changes to verified.
- If rejected, the payment remains pending or needs correction.
- This feature prevents false payment claims.

---

## 5.11 Payment History

Users should be able to view their past payment records.

### Requirements

- Display completed payments.
- Display pending payments.
- Show payment date and proof if available.
- Show payment verification status.
- Allow users to filter payment history by group, date, or category.

---

## 5.12 Notifications

The system should notify users about important payment activities.

### Notification Examples

- New expense added
- User added to an expense
- Payment pending
- Payment marked as paid
- Payment proof uploaded
- Payment verified or rejected

### Requirements

- Users should receive notifications inside the system.
- Notifications should be clear and easy to understand.
- Future improvement can include email notifications.

---

## 5.13 Group-wise Expense Summary

Users should be able to view summaries for each group.

### Summary Should Include

- Total group expenses
- Amount paid by each member
- Amount owed by each member
- Pending payments
- Verified payments

---

## 5.14 Monthly Spending Reports

The system should provide monthly expense reports.

### Report Should Include

- Total monthly spending
- Category-wise spending
- Group-wise spending
- Pending and completed payments
- Highest expense category

---

## 6. User Flow

## 6.1 New User Flow

1. User registers an account.
2. User logs in.
3. User accesses personal dashboard.
4. User creates or joins an expense group.
5. User views group expenses and payment status.

---

## 6.2 Add Expense Flow

1. User selects a group.
2. User clicks “Add Expense”.
3. User enters expense details.
4. User selects participants.
5. System calculates each person’s share.
6. Expense is saved and shown to all selected participants.

---

## 6.3 Payment Settlement Flow

1. User views pending payment.
2. User settles payment outside the system.
3. User marks payment as paid.
4. User uploads proof of payment.
5. Receiver reviews the proof.
6. Receiver confirms or rejects the payment.
7. System updates payment status.

---

## 7. Functional Requirements

The system should allow users to:

- Register and log in
- Access a personal dashboard
- Create expense groups
- Add users to groups
- Add shared expenses
- Select expense participants
- Automatically calculate split amounts
- Track payment status
- Upload payment proof
- Confirm received payments
- View payment history
- Receive notifications
- View group-wise summaries
- View monthly reports

---

## 8. Non-Functional Requirements

The system should be:

- User-friendly
- Responsive on desktop and mobile devices
- Secure for user login and uploaded files
- Easy to navigate
- Fast enough for normal usage
- Reliable in calculating expense balances
- Clear in displaying payment status

---

## 9. User Roles

## 9.1 Normal User

A normal user can:

- Register and log in
- Join groups
- View assigned expenses
- Mark payments as paid
- Upload proof
- View payment history

## 9.2 Group Creator / Admin

A group creator can:

- Create groups
- Add members
- Add expenses
- Manage group details
- View group summaries
- Confirm received payments where applicable

---

## 10. Main Screens

The application should include the following screens:

1. Login Page
2. Register Page
3. User Dashboard
4. Group List Page
5. Group Details Page
6. Add Expense Page
7. Expense Details Page
8. Payment Proof Upload Page
9. Payment History Page
10. Monthly Report Page
11. Notifications Page

---

## 11. MVP Scope

The first version of the system should include only the most important features.

### MVP Features

- User registration and login
- Personal dashboard
- Create expense group
- Add members to group
- Add expense
- Equal split calculation
- Payment status: Pending and Paid
- Payment proof upload
- Basic payment history
- Group-wise expense summary

---

## 12. Future Enhancements

Future improvements can include:

- Custom split amounts
- Email notifications
- Mobile application version
- Recurring expenses
- Export reports as PDF
- Advanced analytics
- Payment gateway integration
- In-app chat or comments
- Reminder scheduling
- Dark mode

---

## 13. Success Metrics

The success of the system can be measured by:

- Users can easily add and track expenses
- Users can clearly understand who owes whom
- Payment status is updated accurately
- Payment proof improves transparency
- Users spend less time calculating shared expenses manually
- Group expense summaries are easy to understand

---

## 14. Conclusion

The Shared Expense Tracking and Payment Verification System is a practical solution for managing shared expenses among groups. By combining expense tracking, automatic split calculation, payment status updates, proof uploads, and payment confirmation, the system provides a transparent and organized way to manage group finances.

This project solves a real-world problem and is suitable for students, roommates, friends, and teams who need a simple and reliable way to track shared expenses.
