# chatbot_banhpia_tranmyhuong.py
import os
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import telegram
from telegram import Bot
from facebook import GraphAPI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Initialize Facebook Graph API
graph = GraphAPI(access_token=FACEBOOK_ACCESS_TOKEN)

# Define a function to return an image URL
def get_image_url():
    return "https://example.com/banh_pia_tran_my_huong.jpg"  # Replace with your actual image URL

# Define a function to normalize input (remove diacritics)
def normalize_input(text):
    return text.normalize('NFKD').encode('ascii', 'ignore').decode('ascii')

# Define a function to handle user input
def chatbot_response(user_input):
    normalized_input = normalize_input(user_input)

    # Define product details
    product_name = "Bánh Pía Trần Mỹ Hương"
    product_price_per_tree = 35000  # 35,000 VND/cây
    combo_price = 100000  # 100,000 VND/3 cây

    # Use GPT-4o mini to interpret the user's message
    prompt = f"Phân tích nội dung sau: '{user_input}' và trả về thông tin về số lượng combo hoặc số lượng cây, nếu có. Nếu không có, hãy trả về 'None'."
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0
    )

    # Extract the response from GPT
    gpt_output = response.choices[0].message.content.strip()

    # Define a function to parse the GPT response
    def parse_gpt_response(gpt_output):
        if "combo" in gpt_output:
            try:
                combo_count = int(gpt_output.split("combo")[0].strip())
                return {"combo": combo_count}
            except:
                return None
        elif "cây" in gpt_output or "cay" in gpt_output:
            try:
                tree_count = int(gpt_output.split("cây")[0].strip())
                return {"tree": tree_count}
            except:
                return None
        else:
            return None

    # Parse GPT's output
    parsed_result = parse_gpt_response(gpt_output)

    # Based on the parsed result, generate response
    if parsed_result:
        if "combo" in parsed_result:
            combo_count = parsed_result["combo"]
            total_combo_price = f"{combo_count * combo_price} VND"
            total_trees = f"{combo_count * 3} cây"
            return f"💰 Giá cho {combo_count} combo: {total_combo_price} (tương đương {total_trees}).\n\n📞 Vui lòng cung cấp số điện thoại và địa chỉ để chúng tôi lên đơn cho bạn."
        elif "tree" in parsed_result:
            tree_count = parsed_result["tree"]
            total_tree_price = tree_count * product_price_per_tree
            combo_count = tree_count // 3
            remaining_trees = tree_count % 3

            # Tính giá theo combo và cây còn lại
            combo_price_total = combo_count * combo_price
            remaining_price_total = remaining_trees * product_price_per_tree

            # Đề xuất nếu có thể mua thêm 1 cây để tạo combo
            if remaining_trees == 2:
                suggested_tree_count = tree_count + 1
                suggested_combo_count = (suggested_tree_count) // 3
                suggested_price = suggested_combo_count * combo_price
                return f"💰 Giá cho {tree_count} cây: {total_tree_price} VND.\n\n💡 Gợi ý: Nếu bạn mua thêm 1 cây, bạn sẽ có {suggested_combo_count} combo ({suggested_combo_count * 3} cây) với giá {suggested_price} VND – tiết kiệm {total_tree_price - suggested_price} VND!\n\n📞 Vui lòng cung cấp số điện thoại và địa chỉ để chúng tôi lên đơn cho bạn."

            # Nếu không có gợi ý (ví dụ: 1 cây hoặc 3 cây)
            return f"💰 Giá cho {tree_count} cây: {total_tree_price} VND.\n\n📞 Vui lòng cung cấp số điện thoại và địa chỉ để chúng tôi lên đơn cho bạn."
    else:
        # If no quantity or combo is detected, default to general info
        return f"💰 Giá: {product_price_per_tree} VND/cây hoặc {combo_price} VND cho combo 3 cây.\n\n📞 Vui lòng cung cấp số điện thoại và địa chỉ để chúng tôi lên đơn cho bạn."

    # Check if the user asked for the image (normalized)
    if "hinh anh" in normalized_input or "anh" in normalized_input:
        return f"🖼️ Đây là hình ảnh: {get_image_url()}"

    # Check if the user wants to place an order (normalized)
    if "dat hang" in normalized_input or "mua" in normalized_input:
        return "📞 Vui lòng cung cấp số điện thoại và địa chỉ để xác nhận đơn hàng."

    # Otherwise, prompt for phone and address even if not placing an order
    return "📞 Vui lòng cung cấp số điện thoại và địa chỉ để chúng tôi hỗ trợ bạn tốt hơn."

# Main loop (example)
async def main():
    try:
        # Example: Read messages from Facebook
        messages = graph.get_object(f"{FACEBOOK_PAGE_ID}/conversations", fields="participants,messages")
        for conversation in messages["data"]:
            for message in conversation["messages"]["data"]:
                if message["from"]["id"] != FACEBOOK_PAGE_ID:
                    user_message = message["message"]
                    print(f"Facebook user: {user_message}")
                    bot_response = chatbot_response(user_message)
                    # Send response to the user on Facebook
                    graph.put_object(f"{FACEBOOK_PAGE_ID}/conversations/{conversation['id']}", "message", {"message": bot_response})
    except Exception as e:
        # Notify via Telegram when an error occurs
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"⚠️ LỖI: {str(e)}")
        print("❌ Có lỗi xảy ra. Đã thông báo qua Telegram. Vui lòng vào chat thật để hỗ trợ.")

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())