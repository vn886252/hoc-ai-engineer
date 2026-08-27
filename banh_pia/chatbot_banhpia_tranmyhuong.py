# chatbot_banhpia_tranmyhuong.py
import os
import time
import asyncio
import json
import unicodedata
from openai import OpenAI
from dotenv import load_dotenv
from telegram import Bot
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import facebook  # pip install facebook-sdk

# ==== Load environment variables ====
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
VERIFY_TOKEN = ("1234")

# ==== Khởi tạo Telegram + Facebook ====
bot = Bot(token=TELEGRAM_BOT_TOKEN)
graph = facebook.GraphAPI(access_token=FACEBOOK_ACCESS_TOKEN)

# Ghi nhớ tin nhắn đã trả lời trong phiên chạy này (tránh trả lời lặp lại)
# Lưu ý: set này chỉ tồn tại trong RAM, restart bot là mất hết.
# Nếu cần chạy production thật, nên lưu vào file/DB (SQLite, Redis, ...) hoặc chuyển sang webhook.
processed_message_ids = set()

PRODUCT_NAME = "Bánh Pía Trần Mỹ Hương"
PRICE_PER_TREE = 35000   # 35.000 VND / cây
COMBO_PRICE = 100000     # 100.000 VND / combo 3 cây
IMAGE_URL = "https://example.com/banh_pia_tran_my_huong.jpg"  # TODO: thay bằng link ảnh thật


def format_vnd(amount: int) -> str:
    """Format số tiền kiểu Việt Nam: 100000 -> 100.000"""
    return f"{amount:,}".replace(",", ".") + " VND"


def normalize_input(text: str) -> str:
    """Bỏ dấu tiếng Việt để so khớp từ khóa dễ hơn."""
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii').lower()


def parse_gpt_response(gpt_output: str):
    """Đọc câu trả lời của GPT và tách ra số combo hoặc số cây."""
    text = gpt_output.strip().lower()
    if "none" in text:
        return None
    if "combo" in text:
        try:
            combo_count = int(text.split("combo")[0].strip())
            return {"combo": combo_count}
        except ValueError:
            return None
    if "cay" in text or "cây" in gpt_output:
        try:
            tree_count = int(text.split("cay")[0].strip())
            return {"tree": tree_count}
        except ValueError:
            return None
    return None


def build_price_reply(user_input: str) -> str:
    """Hỏi GPT để lấy số lượng, rồi tính giá."""
    prompt = (
        f"Phân tích nội dung sau: '{user_input}' và trả về thông tin về số lượng combo "
        f"hoặc số lượng cây, nếu có. Nếu không có, hãy trả về 'None'."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0,
    )
    gpt_output = response.choices[0].message.content.strip()
    parsed_result = parse_gpt_response(gpt_output)

    contact_line = "\n\n📞 Vui lòng cung cấp số điện thoại và địa chỉ để chúng tôi lên đơn cho bạn."

    if not parsed_result:
        return (
            f"💰 Giá: {format_vnd(PRICE_PER_TREE)}/cây hoặc {format_vnd(COMBO_PRICE)} "
            f"cho combo 3 cây.{contact_line}"
        )

    if "combo" in parsed_result:
        combo_count = parsed_result["combo"]
        total_price = combo_count * COMBO_PRICE
        total_trees = combo_count * 3
        return (
            f"💰 Giá cho {combo_count} combo: {format_vnd(total_price)} "
            f"(tương đương {total_trees} cây).{contact_line}"
        )

    # parsed_result có "tree"
    tree_count = parsed_result["tree"]
    total_tree_price = tree_count * PRICE_PER_TREE
    combo_count = tree_count // 3
    remaining_trees = tree_count % 3

    if remaining_trees == 2:
        suggested_tree_count = tree_count + 1
        suggested_combo_count = suggested_tree_count // 3
        suggested_price = suggested_combo_count * COMBO_PRICE
        saved = total_tree_price - suggested_price
        return (
            f"💰 Giá cho {tree_count} cây: {format_vnd(total_tree_price)}.\n\n"
            f"💡 Gợi ý: Nếu bạn mua thêm 1 cây, bạn sẽ có {suggested_combo_count} combo "
            f"({suggested_combo_count * 3} cây) với giá {format_vnd(suggested_price)} "
            f"– tiết kiệm {format_vnd(saved)}!{contact_line}"
        )

    return f"💰 Giá cho {tree_count} cây: {format_vnd(total_tree_price)}.{contact_line}"


def chatbot_response(user_input: str) -> str:
    normalized_input = normalize_input(user_input)

    # 1) Khách hỏi hình ảnh -> trả ảnh ngay, không cần hỏi GPT
    if "hinh anh" in normalized_input or normalized_input.strip() == "anh" or "cho xin anh" in normalized_input:
        return f"🖼️ Đây là hình ảnh {PRODUCT_NAME}: {IMAGE_URL}"

    # 2) Còn lại -> để GPT phân tích số lượng và trả lời giá (đường mặc định,
    #    câu trả lời cuối cùng luôn xin số điện thoại + địa chỉ, nên tự động
    #    xử lý luôn trường hợp khách gõ "đặt hàng" / "mua")
    return build_price_reply(user_input)

async def notify_telegram_error(err: Exception):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ LỖI: {str(err)}")
    except Exception as telegram_err:
        # Nếu Telegram cũng lỗi thì chỉ log ra console, tránh crash toàn bộ chương trình
        print(f"❌ Không gửi được thông báo Telegram: {telegram_err}")

def handle_webhook(request_data):
    for entry in request_data.get('entry', []):
        for messaging_event in entry.get('messaging', []):
            message = messaging_event.get('message', {})
            sender_id = messaging_event.get('sender', {}).get('id')
            if not message.get('text'):
                continue
            if message.get('is_echo'):
                continue
            mid =message.get('mid','')
            if mid and mid in processed_message_ids:
                continue
            if mid:
                processed_message_ids.add(mid)

            user_message = message.get('text', '')
            print(f"Facebook user: {user_message}")
            bot_response = chatbot_response(user_message)

            graph.put_object(
                parent_object="me",
                connection_name="messages",
                recipient=json.dumps({"id":sender_id}),
                message=json.dumps({"text": bot_response})
            )

            # Ghi lại message_id đã xử lý
            processed_message_ids.add(message.get('mid', ''))

app = FastAPI()
@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        handle_webhook(data)
        return JSONResponse(status_code=200, content={"status": "ok"})
    except Exception as e:
        print(f"❌ Error in webhook: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return int(params.get("hub.challenge"))
    raise HTTPException(status_code=403, detail="Verification failed")

if __name__ == "__main__":
    # Chạy FastAPI app
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

async def check_and_reply_once():
    """Quét conversations 1 lượt, trả lời tin nhắn mới chưa xử lý."""
    try:
        messages = graph.get_object(
            f"{FACEBOOK_PAGE_ID}/conversations", fields="participants,messages"
        )
        for conversation in messages.get("data", []):
            for message in conversation.get("messages", {}).get("data", []):
                message_id = message.get("id")
                if message_id in processed_message_ids:
                    continue
                if message.get("from", {}).get("id") == FACEBOOK_PAGE_ID:
                    continue  # bỏ qua tin nhắn do chính page gửi

                user_message = message.get("message", "")
                print(f"Facebook user: {user_message}")
                bot_response = chatbot_response(user_message)

                graph.put_object(
                    f"{FACEBOOK_PAGE_ID}/conversations/{conversation['id']}",
                    "message",
                    {"message": bot_response},
                )
                processed_message_ids.add(message_id)
    except Exception as e:
        await notify_telegram_error(e)
        print("❌ Có lỗi xảy ra. Đã thông báo qua Telegram. Vui lòng vào chat thật để hỗ trợ.")
