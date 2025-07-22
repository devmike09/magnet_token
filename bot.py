import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import psycopg2
from psycopg2 import sql

# Configuration
BOT_TOKEN = os.getenv('MAGNET_BOT')
DB_URL = os.getenv('DATABASE_URL')
CHANNEL_LINK = "https://t.me/signalxmi"
GROUP_LINK = "https://t.me/+pJBigpG3O8c4ZTc0"
TWITTER_LINK = "https://x.com/chaels_001"
MEDIUM_LINK = "https://medium.com/your_profile"

# Database setup
def create_tables():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        username VARCHAR(255),
        balance FLOAT DEFAULT 0,
        referrals INT DEFAULT 0,
        wallet_address VARCHAR(255),
        completed_tasks JSONB
    );
    CREATE TABLE IF NOT EXISTS referrals (
        referrer_id BIGINT,
        referred_id BIGINT,
        PRIMARY KEY (referrer_id, referred_id)
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Check if referral link used
    ref_code = context.args[0] if context.args else None
    if ref_code and ref_code.startswith('ref_'):
        referrer_id = int(ref_code.split('_')[1])
        
        # Add referral if new user
        try:
            conn = psycopg2.connect(DB_URL)
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO referrals (referrer_id, referred_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """, (referrer_id, user_id))
            
            # Update referrer's balance
            cur.execute("""
            UPDATE users 
            SET referrals = referrals + 1,
                balance = balance + 3
            WHERE user_id = %s
            """, (referrer_id,))
            conn.commit()
        finally:
            cur.close()
            conn.close()
    
    # Create user if new
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO users (user_id, username)
    VALUES (%s, %s)
    ON CONFLICT (user_id) DO UPDATE
    SET username = EXCLUDED.username
    RETURNING *
    """, (user_id, username))
    conn.commit()
    cur.close()
    conn.close()
    
    # Send welcome message
    keyboard = [
        [InlineKeyboardButton("✅ Start Airdrop", callback_data='start_airdrop')],
        [InlineKeyboardButton("👥 My Referrals", callback_data='my_referrals')]
    ]
    await update.message.reply_text(
        "🌟 Welcome to Airdrop Bot!\n\n"
        "Earn $1 for each task completed\n"
        "Earn $3 for each referral\n\n"
        "You need 10 referrals to withdraw",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Task handler
async def handle_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    # Task 1: Join Channel
    if query.data == 'start_airdrop':
        keyboard = [[InlineKeyboardButton("Join Channel", url=https://t.me/signalxmi)]]
        await query.edit_message_text(
            "📢 Task 1/3: Join our Telegram Channel\n"
            f"Link: {https://t.me/signalxmi}\n\n"
            "Click below to join then press Done",
            reply_markup=InlineKeyboardMarkup([
                *keyboard,
                [InlineKeyboardButton("✅ Done", callback_data='task1_done')]
            ])
        )
    
    # Task 1 Complete
    elif query.data == 'task1_done':
        # Update balance and mark task complete
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("""
        UPDATE users 
        SET balance = balance + 1,
            completed_tasks = COALESCE(completed_tasks, '{}'::jsonb) || '{"channel": true}'::jsonb
        WHERE user_id = %s
        """, (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        
        # Task 2: Join Group
        keyboard = [[InlineKeyboardButton("Join Group", url=https://t.me/+pJBigpG3O8c4ZTc0)]]
        await query.edit_message_text(
            "👥 Task 2/3: Join our Telegram Group\n"
            f"Link: {https://t.me/+pJBigpG3O8c4ZTc0}\n\n"
            "⚠️ Hope you didn't cheat the system; all tasks will be verified manually before your airdrop withdrawal is processed\n\n"
            "Click below to join then press Done",
            reply_markup=InlineKeyboardMarkup([
                *keyboard,
                [InlineKeyboardButton("✅ Done", callback_data='task2_done')]
            ])
        )
    
    # Task 2 Complete
    elif query.data == 'task2_done':
        # Update balance
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("""
        UPDATE users 
        SET balance = balance + 1,
            completed_tasks = completed_tasks || '{"group": true}'::jsonb
        WHERE user_id = %s
        """, (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        
        # Task 3: Follow Socials
        await query.edit_message_text(
            "🔗 Task 3/3: Follow us on Social Media\n\n"
            f"Twitter: {https://x.com/chaels_001}\n"
            f"Medium: {https://x.com/chaels_001}\n\n"
            "Press Done after following both",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Done", callback_data='task3_done')]
            ])
        )
    
    # Task 3 Complete
    elif query.data == 'task3_done':
        # Update balance
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("""
        UPDATE users 
        SET balance = balance + 1,
            completed_tasks = completed_tasks || '{"social": true}'::jsonb
        WHERE user_id = %s
        """, (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        
        # Generate referral link
        ref_link = f"https://t.me/{context.bot.username}?start=ref_{user_id}"
        
        await query.edit_message_text(
            "🎉 All tasks completed! $3 added to your balance\n\n"
            "📊 Current Balance: $3\n"
            "👥 Referrals: 0/10\n\n"
            f"🔗 Your referral link:\n{ref_link}\n\n"
            "Invite friends to earn $3 per referral",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👥 My Referrals", callback_data='my_referrals')]
            ])
        )

# Referral handler
async def handle_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    # Get referral data
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("""
    SELECT referrals, balance 
    FROM users 
    WHERE user_id = %s
    """, (user_id,))
    data = cur.fetchone()
    referrals, balance = data if data else (0, 0)
    cur.close()
    conn.close()
    
    ref_link = f"https://t.me/{context.bot.username}?start=ref_{user_id}"
    
    await query.edit_message_text(
        f"📊 Referral Stats\n\n"
        f"👥 Total Referrals: {referrals}\n"
        f"💰 Earned from referrals: ${referrals * 3}\n"
        f"💵 Total Balance: ${balance}\n\n"
        f"🔗 Your referral link:\n{ref_link}\n\n"
        "You need 10 referrals to withdraw",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Back", callback_data='back_to_main')]
        ])
    )

# Wallet address handler
async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    wallet_address = update.message.text.strip()
    
    # Save wallet address
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("""
    UPDATE users 
    SET wallet_address = %s
    WHERE user_id = %s
    """, (wallet_address, user_id))
    conn.commit()
    
    # Check referrals
    cur.execute("SELECT referrals FROM users WHERE user_id = %s", (user_id,))
    referrals = cur.fetchone()[0]
    cur.close()
    conn.close()
    
    if referrals >= 10:
        await update.message.reply_text(
            "✅ Wallet address saved!\n\n"
            "Your withdrawal request has been queued for manual verification. "
            "We'll notify you once processed."
        )
    else:
        await update.message.reply_text(
            "✅ Wallet address saved!\n\n"
            f"You still need {10 - referrals} more referrals to withdraw. "
            "Keep inviting!"
        )

# Main function
def main():
    create_tables()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_tasks, pattern="^(start_airdrop|task1_done|task2_done|task3_done)"))
    app.add_handler(CallbackQueryHandler(handle_referrals, pattern="^(my_referrals|back_to_main)"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet))
    
    app.run_polling()

if __name__ == '__main__':
    main()
