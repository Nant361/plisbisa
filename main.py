import multiprocessing
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler
import admin_bot
import telegram_bot
import signal
import sys
import socket
import threading
import os
import http.server
import socketserver
import asyncio
from telegram.error import TimedOut, NetworkError
import time

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Connection settings
CONNECT_TIMEOUT = 30.0
READ_TIMEOUT = 30.0
WRITE_TIMEOUT = 30.0
POOL_TIMEOUT = 30.0
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Simple HTTP Handler for health checks
class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    # Suppress log messages
    def log_message(self, format, *args):
        return

def run_health_check_server():
    """Run a simple TCP and HTTP server for health checks"""
    try:
        # Get port from environment variable or default to 8000
        port = int(os.environ.get('PORT', 8000))
        logger.info(f"Starting health check server on port {port}...")
        
        # Create an HTTP server
        httpd = socketserver.TCPServer(("", port), HealthCheckHandler)
        logger.info(f"HTTP health check server started at port {port}")
        httpd.serve_forever()
                
    except Exception as e:
        logger.error(f"Failed to start health check server: {str(e)}")

def run_admin_bot():
    """Run the admin bot"""
    while True:  # Outer loop for continuous operation
        try:
            logger.info("Starting Admin Bot...")
            application = (
                Application.builder()
                .token(admin_bot.ADMIN_TOKEN)
                .connect_timeout(CONNECT_TIMEOUT)
                .read_timeout(READ_TIMEOUT)
                .write_timeout(WRITE_TIMEOUT)
                .pool_timeout(POOL_TIMEOUT)
                .build()
            )

            # Add handlers
            handlers = [
                CommandHandler("start", admin_bot.start),
                CommandHandler("list", admin_bot.list_users),
                CommandHandler("add", admin_bot.add_user),
                CommandHandler("remove", admin_bot.remove_user),
                CommandHandler("logs", admin_bot.view_logs),
                CommandHandler("getid", admin_bot.get_user_id),
                CommandHandler("chatid", admin_bot.get_chat_id),
                MessageHandler(admin_bot.filters.FORWARDED, admin_bot.get_user_id)
            ]
            
            for handler in handlers:
                application.add_handler(handler)

            logger.info("Admin Bot is ready!")
            application.run_polling(
                allowed_updates=admin_bot.Update.ALL_TYPES,
                drop_pending_updates=True,
                read_timeout=READ_TIMEOUT,
                write_timeout=WRITE_TIMEOUT,
                connect_timeout=CONNECT_TIMEOUT,
                pool_timeout=POOL_TIMEOUT
            )
                
        except (TimedOut, NetworkError) as e:
            logger.warning(f"Connection error occurred: {str(e)}")
            retry_count = 0
            while retry_count < MAX_RETRIES:
                try:
                    logger.info(f"Attempting to reconnect... (Attempt {retry_count + 1}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
                    retry_count += 1
                except Exception as retry_error:
                    logger.error(f"Error during retry attempt: {str(retry_error)}")
                    break
            if retry_count >= MAX_RETRIES:
                logger.error("Max retries reached. Restarting bot...")
                time.sleep(RETRY_DELAY)
                continue
        except Exception as e:
            logger.error(f"Unexpected error in Admin Bot: {str(e)}", exc_info=True)
            time.sleep(RETRY_DELAY)
            continue

def run_student_bot():
    """Run the student search bot"""
    while True:  # Outer loop for continuous operation
        try:
            logger.info("Starting Student Search Bot...")
            application = (
                Application.builder()
                .token(telegram_bot.TOKEN)
                .connect_timeout(CONNECT_TIMEOUT)
                .read_timeout(READ_TIMEOUT)
                .write_timeout(WRITE_TIMEOUT)
                .pool_timeout(POOL_TIMEOUT)
                .build()
            )

            # Add handlers
            handlers = [
                CommandHandler("start", telegram_bot.start),
                CommandHandler("cari", telegram_bot.search),
                CommandHandler("regist", telegram_bot.register_user),
                CallbackQueryHandler(telegram_bot.button_callback),
                MessageHandler(telegram_bot.filters.TEXT & ~telegram_bot.filters.COMMAND, telegram_bot.handle_message),
                MessageHandler(telegram_bot.filters.PHOTO, telegram_bot.handle_message),
                MessageHandler(telegram_bot.filters.Document.ALL, telegram_bot.handle_message),
                MessageHandler(telegram_bot.filters.VOICE, telegram_bot.handle_message),
                MessageHandler(telegram_bot.filters.VIDEO, telegram_bot.handle_message),
                MessageHandler(telegram_bot.filters.Sticker.ALL, telegram_bot.handle_message),
                MessageHandler(telegram_bot.filters.LOCATION, telegram_bot.handle_message),
                MessageHandler(telegram_bot.filters.CONTACT, telegram_bot.handle_message),
                MessageHandler(telegram_bot.filters.ANIMATION, telegram_bot.handle_message),
                MessageHandler(telegram_bot.filters.AUDIO, telegram_bot.handle_message)
            ]
            
            for handler in handlers:
                application.add_handler(handler)

            logger.info("Student Search Bot is ready!")
            application.run_polling(
                allowed_updates=telegram_bot.Update.ALL_TYPES,
                drop_pending_updates=True,
                read_timeout=READ_TIMEOUT,
                write_timeout=WRITE_TIMEOUT,
                connect_timeout=CONNECT_TIMEOUT,
                pool_timeout=POOL_TIMEOUT
            )
                
        except (TimedOut, NetworkError) as e:
            logger.warning(f"Connection error occurred: {str(e)}")
            retry_count = 0
            while retry_count < MAX_RETRIES:
                try:
                    logger.info(f"Attempting to reconnect... (Attempt {retry_count + 1}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
                    retry_count += 1
                except Exception as retry_error:
                    logger.error(f"Error during retry attempt: {str(retry_error)}")
                    break
            if retry_count >= MAX_RETRIES:
                logger.error("Max retries reached. Restarting bot...")
                time.sleep(RETRY_DELAY)
                continue
        except Exception as e:
            logger.error(f"Unexpected error in Student Search Bot: {str(e)}", exc_info=True)
            time.sleep(RETRY_DELAY)
            continue

def signal_handler(signum, frame):
    """Handle termination signals"""
    logger.info("Received termination signal. Shutting down bots...")
    sys.exit(0)

def main():
    """Run both bots concurrently"""
    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Starting both bots...")
        
        # Start health check server in a separate thread
        health_thread = threading.Thread(target=run_health_check_server, daemon=True)
        health_thread.start()
        logger.info("Health check server started")
        
        # Create processes for each bot
        admin_process = multiprocessing.Process(target=run_admin_bot, name="AdminBot")
        student_process = multiprocessing.Process(target=run_student_bot, name="StudentBot")
        
        # Start both processes
        admin_process.start()
        student_process.start()
        
        # Wait for both processes to complete
        admin_process.join()
        student_process.join()
        
    except KeyboardInterrupt:
        logger.info("\nBots stopped by user")
        admin_process.terminate()
        student_process.terminate()
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}", exc_info=True)
        if 'admin_process' in locals():
            admin_process.terminate()
        if 'student_process' in locals():
            student_process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main() 