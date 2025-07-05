export interface ChatEventMap {
	changeConversation: { conversationId: string };
	uploadFiles: { files: File[]; roles: string[] };
	confirmUploadFiles: { result: boolean; error?: Error };
	// thêm các event khác...
}

type EventCallback<T> = (payload: T) => void;

export class EventBus<Events extends Record<string, any>> {
	private subscribers: {
		[K in keyof Events]?: Set<EventCallback<Events[K]>>;
	} = {};

	// Đăng ký lắng nghe event
	on<K extends keyof Events>(eventName: K, callback: EventCallback<Events[K]>): () => void {
		if (!this.subscribers[eventName]) {
			this.subscribers[eventName] = new Set();
		}
		this.subscribers[eventName]!.add(callback);

		// Trả về hàm hủy đăng ký
		return () => {
			this.subscribers[eventName]?.delete(callback);
			if (this.subscribers[eventName]?.size === 0) {
				delete this.subscribers[eventName];
			}
		};
	}

	// Phát event
	emit<K extends keyof Events>(eventName: K, payload: Events[K]): void {
		this.subscribers[eventName]?.forEach((callback) => {
			try {
				callback(payload);
			} catch (error) {
				console.error(`Error in event handler for ${String(eventName)}`, error);
			}
		});
	}
}

// DEMO

// Khởi tạo EventBus với kiểu sự kiện
const eventBus = new EventBus<ChatEventMap>();
export default eventBus;

// Component A phát event
// function ComponentA() {
// 	const handleRegister = () => {
// 		eventBus.emit("changeConversation", { userId: "123", email: "user@example.com" });
// 	};
// }

// // Component B lắng nghe event
// function ComponentB() {
// 	useEffect(() => {
// 		const unsubscribe = eventBus.on("changeConversation", (payload) => {
// 			console.log("User registered:", payload.userId, payload.email);
// 			// Xử lý logic khi có event
// 		});

// 		return () => {
// 			unsubscribe(); // Hủy đăng ký khi component unmount
// 		};
// 	}, []);
// }
