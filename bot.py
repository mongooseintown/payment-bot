import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = '8334842537:AAHS0oEwHEQJrm6V8weTbxCjUcgBjYMOQ4Y'
ADMIN_ID = 5470027353

# Semester and Subject Configuration
SEMESTERS = {
    '1': {'name': 'Semester 1', 'subjects': {'c': 'C Programming', 'ds': 'Data Structures', 'web': 'Web Development'}},
    '2': {'name': 'Semester 2', 'subjects': {'oop': 'OOP', 'db': 'Database', 'web': 'Web Development'}},
    '3': {'name': 'Semester 3', 'subjects': {'java': 'Java', 'ai': 'AI/ML', 'cc': 'Cloud Computing'}},
    '4': {'name': 'Semester 4', 'subjects': {'python': 'Python', 'ml': 'Machine Learning', 'devops': 'DevOps'}},
    '5': {'name': 'Semester 5', 'subjects': {'android': 'Android Dev', 'blockchain': 'Blockchain', 'security': 'Cybersecurity'}},
    '6': {'name': 'Semester 6', 'subjects': {'react': 'React JS', 'backend': 'Backend Dev', 'iot': 'IoT'}},
    '7': {'name': 'Semester 7', 'subjects': {'full_stack': 'Full Stack', 'systems': 'Systems Design', 'ar_vr': 'AR/VR'}},
    '8': {'name': 'Semester 8', 'subjects': {'capstone': 'Capstone Project', 'internship': 'Internship', 'final': 'Final Year Project'}}
}

# Subject Group Links (Update these with your actual group links)
SUBJECT_GROUPS = {
    '1_c': 'https://t.me/+sem1_c_group',
    '1_ds': 'https://t.me/+sem1_ds_group',
    '1_web': 'https://t.me/+lAWD3BLxzF43NjU1',
    '2_oop': 'https://t.me/+sem2_oop_group',
    '2_db': 'https://t.me/+sem2_db_group',
    '2_web': 'https://t.me/+sem2_web_group',
    '3_java': 'https://t.me/+sem3_java_group',
    '3_ai': 'https://t.me/+sem3_ai_group',
    '3_cc': 'https://t.me/+sem3_cc_group',
    '4_python': 'https://t.me/+sem4_python_group',
    '4_ml': 'https://t.me/+sem4_ml_group',
    '4_devops': 'https://t.me/+sem4_devops_group',
    '5_android': 'https://t.me/+sem5_android_group',
    '5_blockchain': 'https://t.me/+sem5_blockchain_group',
    '5_security': 'https://t.me/+sem5_security_group',
    '6_react': 'https://t.me/+sem6_react_group',
    '6_backend': 'https://t.me/+sem6_backend_group',
    '6_iot': 'https://t.me/+sem6_iot_group',
    '7_full_stack': 'https://t.me/+sem7_full_stack_group',
    '7_systems': 'https://t.me/+sem7_systems_group',
    '7_ar_vr': 'https://t.me/+sem7_ar_vr_group',
    '8_capstone': 'https://t.me/+sem8_capstone_group',
    '8_internship': 'https://t.me/+sem8_internship_group',
    '8_final': 'https://t.me/+sem8_final_group',
}

# Store user data and pending approvals
user_data = {}
pending_approvals = {}
approval_counter = 0
student_enrollments = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton("📚 Select Your Semester", callback_data='show_semesters')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Add persistent keyboard button
    persistent_keyboard = [[KeyboardButton("📚 Select Your Semester")]]
    persistent_markup = ReplyKeyboardMarkup(persistent_keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "Click below to select your semester and get access to your subject groups.",
        reply_markup=reply_markup
    )


async def show_semesters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show semester selection."""
    query = update.callback_query
    
    keyboard = []
    for sem_id in sorted(SEMESTERS.keys()):
        sem_name = SEMESTERS[sem_id]['name']
        keyboard.append([InlineKeyboardButton(sem_name, callback_data=f'sem_{sem_id}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📚 Select your semester:",
        reply_markup=reply_markup
    )


async def semester_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle semester selection."""
    query = update.callback_query
    user_id = query.from_user.id
    
    sem_id = query.data.replace('sem_', '')
    
    if sem_id not in SEMESTERS:
        await query.answer("Invalid semester!", show_alert=True)
        return
    
    # Store semester choice
    user_data[user_id] = {'semester': sem_id, 'semester_name': SEMESTERS[sem_id]['name']}
    
    # Show subjects
    subjects = SEMESTERS[sem_id]['subjects']
    keyboard = []
    
    for subject_id, subject_name in subjects.items():
        keyboard.append([InlineKeyboardButton(subject_name, callback_data=f'subject_{sem_id}_{subject_id}')])
    
    keyboard.append([InlineKeyboardButton("« Back", callback_data='back_to_semesters')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📚 {SEMESTERS[sem_id]['name']}\n\n"
        "Select your subject:",
        reply_markup=reply_markup
    )


async def subject_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle subject selection."""
    query = update.callback_query
    user_id = query.from_user.id
    
    data = query.data.replace('subject_', '').split('_', 1)
    sem_id = data[0]
    subject_id = data[1]
    
    subject_name = SEMESTERS[sem_id]['subjects'].get(subject_id, 'Unknown Subject')
    
    # Store subject choice
    if user_id in user_data:
        user_data[user_id]['subject'] = subject_id
        user_data[user_id]['subject_name'] = subject_name
    
    keyboard = [
        [InlineKeyboardButton("« Back", callback_data=f'sem_{sem_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ You selected: {SEMESTERS[sem_id]['name']} - {subject_name}\n\n"
        f"💰 Now please send your payment screenshot to confirm your enrollment.\n\n"
        f"📸 Just upload an image of your payment receipt below.",
        reply_markup=reply_markup
    )


async def back_to_semesters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Go back to semester selection."""
    query = update.callback_query
    
    keyboard = []
    for sem_id in sorted(SEMESTERS.keys()):
        sem_name = SEMESTERS[sem_id]['name']
        keyboard.append([InlineKeyboardButton(sem_name, callback_data=f'sem_{sem_id}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📚 Select your semester:",
        reply_markup=reply_markup
    )


async def handle_semester_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the persistent semester button."""
    keyboard = []
    for sem_id in sorted(SEMESTERS.keys()):
        sem_name = SEMESTERS[sem_id]['name']
        keyboard.append([InlineKeyboardButton(sem_name, callback_data=f'sem_{sem_id}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📚 Select your semester:",
        reply_markup=reply_markup
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle payment screenshot submissions."""
    global approval_counter
    user = update.message.from_user
    user_id = user.id
    
    if user_id not in user_data or 'subject' not in user_data[user_id]:
        # Add persistent keyboard
        keyboard = [[KeyboardButton("📚 Select Your Semester")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "⚠️ Please select a semester and subject first!",
            reply_markup=reply_markup
        )
        return
    
    # Get the photo
    photo = update.message.photo[-1]
    file_id = photo.file_id
    
    # Use simple counter
    approval_counter += 1
    approval_id = str(approval_counter)
    
    user_info = user_data[user_id]
    
    # Get full name
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    if not full_name:
        full_name = user.first_name or f"User_{user_id}"
    
    # Store approval data
    pending_approvals[approval_id] = {
        'user_id': user_id,
        'username': user.username or "No Username",
        'full_name': full_name,
        'file_id': file_id,
        'semester': user_info['semester'],
        'semester_name': user_info['semester_name'],
        'subject': user_info['subject'],
        'subject_name': user_info['subject_name']
    }
    
    # Acknowledge receipt
    await update.message.reply_text(
        f"✅ Payment screenshot received!\n"
        f"📚 Semester: {user_info['semester_name']}\n"
        f"📖 Subject: {user_info['subject_name']}\n\n"
        f"⏳ Admin will review it shortly."
    )
    
    # Send to admin with approval buttons
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f'approve_{approval_id}'),
            InlineKeyboardButton("❌ Reject", callback_data=f'reject_{approval_id}')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    caption = (
        f"📋 Payment Approval Request\n\n"
        f"👤 Full Name: {full_name}\n"
        f"👥 Username: @{user.username or 'Not Set'}\n"
        f"🆔 User ID: {user_id}\n"
        f"📚 Semester: {user_info['semester_name']}\n"
        f"📖 Subject: {user_info['subject_name']}\n"
        f"⏰ Status: ⏳ Pending"
    )
    
    try:
        print(f"Attempting to send photo to ADMIN_ID: {ADMIN_ID}")
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=file_id,
            caption=caption,
            reply_markup=reply_markup
        )
        logger.info(f"Photo sent to admin from user {user_id}")
    except Exception as e:
        error_msg = str(e)
        print(f"ERROR DETAILS: {error_msg}")
        logger.error(f"Error sending photo to admin: {error_msg}")
        await update.message.reply_text(
            f"❌ Error: {error_msg}"
        )


async def approve_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Approve payment and send group link."""
    query = update.callback_query
    
    approval_id = query.data.replace('approve_', '')
    
    if approval_id not in pending_approvals:
        await query.answer("Payment record not found!", show_alert=True)
        return
    
    approval_info = pending_approvals[approval_id]
    user_id = approval_info['user_id']
    full_name = approval_info['full_name']
    username = approval_info['username']
    semester = approval_info['semester']
    subject = approval_info['subject']
    subject_name = approval_info['subject_name']
    semester_name = approval_info['semester_name']
    
    # Get the group link
    group_key = f"{semester}_{subject}"
    base_group_link = SUBJECT_GROUPS.get(group_key, 'https://t.me/default_group')
    
    # Create a unique enrollment record for this student
    enrollment_key = f"{user_id}_{semester}_{subject}"
    student_enrollments[enrollment_key] = {
        'user_id': user_id,
        'username': username,
        'full_name': full_name,
        'semester': semester,
        'subject': subject,
        'approved': True
    }
    
    try:
        # Send group link with security notice
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Payment Approved!\n\n"
                 f"🎉 Welcome to {semester_name} - {subject_name}\n\n"
                 f"🔗 Group Link:\n{base_group_link}\n\n"
                 f"⚠️ Security Notice:\n"
                 f"• This link is personalized for you\n"
                 f"• Do not share it with others\n"
                 f"• Sharing violates our terms\n\n"
                 f"See you in the group! 👋"
        )
        
        # Update admin message
        await query.edit_message_caption(
            caption=f"📋 Payment Approval Request\n\n"
                    f"👤 Full Name: {full_name}\n"
                    f"👥 Username: @{username}\n"
                    f"🆔 User ID: {user_id}\n"
                    f"📚 Semester: {semester_name}\n"
                    f"📖 Subject: {subject_name}\n"
                    f"⏰ Status: ✅ APPROVED\n"
                    f"✓ Link sent to student",
            reply_markup=None
        )
        
        await query.answer("Payment approved! Link sent! ✅", show_alert=False)
        logger.info(f"Payment approved for user {user_id} - {semester_name} - {subject_name}")
        
        # Clean up
        del pending_approvals[approval_id]
        
    except Exception as e:
        logger.error(f"Error approving payment: {e}")
        await query.answer("Error sending group link!", show_alert=True)


async def reject_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reject payment."""
    query = update.callback_query
    
    approval_id = query.data.replace('reject_', '')
    
    if approval_id not in pending_approvals:
        await query.answer("Payment record not found!", show_alert=True)
        return
    
    approval_info = pending_approvals[approval_id]
    user_id = approval_info['user_id']
    full_name = approval_info['full_name']
    username = approval_info['username']
    semester_name = approval_info['semester_name']
    subject_name = approval_info['subject_name']
    
    try:
        # Send rejection message to student
        await context.bot.send_message(
            chat_id=user_id,
            text=f"❌ Payment Rejected\n\n"
                 f"Your payment for {semester_name} - {subject_name} could not be verified.\n\n"
                 f"Please check your payment details and contact admin for assistance."
        )
        
        # Update admin message
        await query.edit_message_caption(
            caption=f"📋 Payment Approval Request\n\n"
                    f"👤 Full Name: {full_name}\n"
                    f"👥 Username: @{username}\n"
                    f"🆔 User ID: {user_id}\n"
                    f"📚 Semester: {semester_name}\n"
                    f"📖 Subject: {subject_name}\n"
                    f"⏰ Status: ❌ REJECTED",
            reply_markup=None
        )
        
        await query.answer("Payment rejected! ❌", show_alert=False)
        
        # Clean up
        del pending_approvals[approval_id]
        
    except Exception as e:
        logger.error(f"Error rejecting payment: {e}")
        await query.answer("Error sending rejection message!", show_alert=True)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Exception while handling an update: {context.error}")


def main() -> None:
    """Start the bot."""
    
    if not BOT_TOKEN or not ADMIN_ID:
        print("❌ Error: Missing BOT_TOKEN or ADMIN_ID!")
        return
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("select_your_semester", start))
    application.add_handler(MessageHandler(filters.Text("📚 Select Your Semester"), handle_semester_button))
    application.add_handler(CallbackQueryHandler(show_semesters, pattern='^show_semesters$'))
    application.add_handler(CallbackQueryHandler(semester_selected, pattern='^sem_'))
    application.add_handler(CallbackQueryHandler(subject_selected, pattern='^subject_'))
    application.add_handler(CallbackQueryHandler(back_to_semesters, pattern='^back_to_semesters$'))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(approve_payment, pattern='^approve_'))
    application.add_handler(CallbackQueryHandler(reject_payment, pattern='^reject_'))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot
    print("🤖 Bot started! Press Ctrl+C to stop.")
    application.run_polling()


if __name__ == '__main__':
    main()