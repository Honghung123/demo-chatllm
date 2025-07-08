"use client";

import type React from "react";

import { chatStreamingResponse, getAllAiModels, getChatHistory } from "@/api/chat.api";
import { ChatMessage } from "@/app/(pages)/chat/chat-message";
import GptSvg from "@/assets/svg/gpt.svg";
import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { LoadingOverlay } from "@/components/ui/loading-circle";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar";
import { Textarea } from "@/components/ui/textarea";
import { AIModel, ChatRequestType, MessageType } from "@/types/chat.type";
import { UserType } from "@/types/user.type";
import { formatDistanceToNow } from "date-fns";
import { Check, ChevronDown, LogOut, Plus, Send, Settings, StopCircle } from "lucide-react";
import Image from "next/image";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { remark } from "remark";
import html from "remark-html";
import eventBus from "@/hooks/event-bus";
import UploadFileModal from "@/app/(pages)/chat/upload-files";
import { RespondingAnimation } from "@/components/ui/responding-animation";

interface ChatMainProps {
	user: UserType;
}

export function ChatMain({ user }: ChatMainProps) {
	const router = useRouter();
	const [conversationId, setConversationId] = useState<string | null>(null);
	const [aiModels, setAiModels] = useState<AIModel[]>([]);
	const [selectedModel, setSelectedModel] = useState<AIModel | null>(null);
	const [messages, setMessages] = useState<MessageType[]>([]);
	const [isLoadingPage, setIsLoadingPage] = useState(true);
	const [input, setInput] = useState("Read sales.txt and suggest compaigns.");
	const [isChatResponding, setIsChatResponding] = useState(false);
	const [isTyping, setIsTyping] = useState(false);
	const textareaRef = useRef<HTMLTextAreaElement>(null);
	const scrollAreaRef = useRef<HTMLDivElement>(null);
	const controllerRef = useRef<AbortController | null>(null);

	useEffect(() => {
		const loadModels = async () => {
			const models = await getAllAiModels();
			setAiModels(models);
			setSelectedModel(models[0]);
		};
		loadModels();
		controllerRef.current = new AbortController();
		return () => {
			controllerRef.current!.abort();
		};
	}, []);

	useEffect(() => {
		const unsubscribe = eventBus.on("changeConversation", async (payload) => {
			const chatHistory = await getChatHistory(user.id, payload.conversationId);
			setMessages(chatHistory);
			setConversationId(payload.conversationId!);
			scrollToBottom();
			setIsLoadingPage(false);
		});
		return () => {
			unsubscribe();
		};
	}, []);

	const scrollToBottom = () => {
		if (scrollAreaRef.current) {
			const scrollContainer = scrollAreaRef.current.querySelector("[data-radix-scroll-area-viewport]");
			if (scrollContainer) {
				scrollContainer.scrollTo({
					top: scrollContainer.scrollHeight,
					behavior: "smooth",
				});
			}
		}
	};

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!input.trim() || isChatResponding) return;
		scrollToBottom();
		const userMessage: MessageType = {
			id: `${messages.length + 1}`,
			role: "user",
			content: input.trim(),
			timestamp: formatDistanceToNow(new Date(), { addSuffix: true }),
		};

		setMessages((prev) => [...prev, userMessage]);
		setInput("");
		setIsChatResponding(true);
		const request: ChatRequestType = {
			userId: user.id,
			username: user.username,
			userRole: user.role,
			conversationId: conversationId!,
			role: userMessage.role,
			content: userMessage.content,
			history: [],
			model: selectedModel!.model,
			modelName: selectedModel!.modelName,
		};

		try {
			const response = await chatStreamingResponse(request, controllerRef.current!);
			if (!response.body) {
				throw new Error("An error occurred from server. Please try again.");
			}
			const reader = response.body.getReader();
			const decoder = new TextDecoder();
			let done = false;
			let assistantMessage = "";

			while (!done) {
				const { value, done: doneReading } = await reader.read();
				setIsTyping(true);
				done = doneReading;
				const chunk = decoder.decode(value, { stream: true });
				// chunk có dạng: data: {"content":"some text"}\n\n
				const lines = chunk.split("\n").filter(Boolean);
				for (const line of lines) {
					if (line.startsWith("data: ")) {
						const jsonStr = line.replace("data: ", "");
						try {
							const data = JSON.parse(jsonStr);
							assistantMessage += data.content;
							const processedContent = await remark().use(html).process(assistantMessage);
							const assistantContentHtml = processedContent.toString();
							setMessages((prev) => {
								// Cập nhật tin nhắn assistant cuối cùng hoặc thêm mới
								if (prev.length > 0 && prev[prev.length - 1].role === "assistant") {
									const newPrev = [...prev];
									newPrev[newPrev.length - 1].content = assistantContentHtml;
									return newPrev;
								} else {
									return [
										...prev,
										{
											id: `${messages.length + 2}`,
											role: "assistant",
											content: assistantContentHtml,
											timestamp: formatDistanceToNow(new Date(), { addSuffix: true }),
											isError: false,
										},
									];
								}
							});
						} catch (e) {
							throw new Error("An error when processing server response. Please try again.");
						}
					}
				}
			}
		} catch (error: any) {
			let errorMessage = "An error occurred while processing your request. Please try again!";
			if (error.name === "AbortError") {
				errorMessage = "You have cancelled the request!";
			} else if (error instanceof Error) {
				errorMessage = error.message;
			}
			setMessages((prev) => {
				if (prev.length > 0 && prev[prev.length - 1].role === "assistant") {
					const newPrev = [...prev];
					newPrev[newPrev.length - 1].content = errorMessage;
					newPrev[newPrev.length - 1].isError = true;
					return newPrev;
				} else {
					return [
						...prev,
						{
							id: `${messages.length + 2}`,
							role: "assistant",
							content: errorMessage,
							timestamp: formatDistanceToNow(new Date(), { addSuffix: true }),
							isError: true,
						},
					];
				}
			});
			controllerRef.current = new AbortController();
		}
		setIsTyping(false);
		setIsChatResponding(false);
	};

	const handleKeyDown = (e: React.KeyboardEvent) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			handleSubmit(e);
		}
	};

	const handleStop = () => {
		try {
			controllerRef.current!.abort();
		} catch (err) {
			console.log("Abort failed!");
		}
	};

	const handleLogout = () => {
		sessionStorage.removeItem("user");
		router.push("/");
	};

	if (isLoadingPage) return <LoadingOverlay text="Loading chat..." />;

	return (
		<SidebarInset className="flex flex-col h-full">
			{/* Header */}
			<div className="flex items-center justify-between p-2 bg-transparent select-none">
				<div className="flex items-center bg-transparent">
					<SidebarTrigger className="mr-4" />
					<DropdownMenu>
						<DropdownMenuTrigger asChild>
							<Button variant="ghost" className="text-lg font-semibold text-gray-900 hover:bg-gray-100 cursor-pointer">
								{selectedModel!.displayName}
								<ChevronDown className="w-4 h-4 ml-1" />
							</Button>
						</DropdownMenuTrigger>
						<DropdownMenuContent align="start" className="w-80">
							{aiModels.map((model, index) => (
								<DropdownMenuItem
									key={index}
									onClick={() => setSelectedModel(model)}
									className="flex items-center justify-between px-4 py-2 cursor-pointer"
								>
									<div className="flex items-center">
										<div>
											<div className="font-medium">{model.displayName}</div>
											<div className="text-sm text-gray-500">{model.description}</div>
										</div>
									</div>
									<div className="flex items-center">
										{selectedModel!.modelName === model.modelName && <Check className="w-4 h-4 text-green-600" />}
									</div>
								</DropdownMenuItem>
							))}
						</DropdownMenuContent>
					</DropdownMenu>
				</div>
				<Button variant="outline" onClick={handleLogout} className="text-gray-700 hover:bg-gray-100 cursor-pointer">
					<LogOut className="w-4 h-4" />
				</Button>
			</div>

			{/* Messages */}
			<ScrollArea ref={scrollAreaRef} className="flex-1 px-4">
				<div className="max-w-3xl mx-auto py-1 space-y-6 max-h-[69vh]">
					{messages.map((message) => (
						<ChatMessage key={message.id} message={message} />
					))}
					{isChatResponding && !isTyping && (
						<div className="flex items-start space-x-2">
							<div className="p-0">
								<Image src={GptSvg} alt="GPT Logo" className="w-6 h-6" />
							</div>
							<div className="flex-1 flex">
								<RespondingAnimation variant="dots" className="text-gray-700" />
							</div>
						</div>
					)}
					{isChatResponding && isTyping && (
						<div className="flex items-start">
							<div className="flex-1 flex">
								<RespondingAnimation variant="dots" className="text-gray-700" />
							</div>
						</div>
					)}
					<div style={{ height: "2rem", visibility: "hidden" }} />
				</div>
			</ScrollArea>

			{/* Input Area */}
			<div className="border-gray-200 p-1">
				<div className="max-w-3xl mx-auto">
					<form onSubmit={handleSubmit} className="border border-gray-300 rounded-2xl">
						<Textarea
							ref={textareaRef}
							value={input}
							onChange={(e) => setInput(e.target.value)}
							onKeyDown={handleKeyDown}
							placeholder={`Message ${selectedModel!.displayName}...`}
							className="min-h-[60px] max-h-[200px] resize-none !border-0 !outline-0 focus:ring-0 focus-visible:ring-0 pb-1"
							disabled={isChatResponding || isTyping}
						/>
						<div className="flex items-center justify-between w-full px-3 py-1">
							<div className="flex">
								<UploadFileModal user={user}>
									<Button
										type="button"
										variant="ghost"
										size="sm"
										className="h-8 w-8 p-0 rounded-full hover:bg-gray-100 cursor-pointer"
									>
										<Plus className="w-4 h-4" />
									</Button>
								</UploadFileModal>

								{/* Tools Button */}
								{/* <Button
									type="button"
									variant="ghost"
									size="sm"
									className="h-8 px-3 rounded-full hover:bg-gray-100 text-gray-600 cursor-pointer"
								>
									<Settings className="w-4 h-4" />
									<span className="text-sm">Tools</span>
								</Button> */}
							</div>
							<div className="flex">
								{isChatResponding || isTyping ? (
									<Button
										type="button"
										size="sm"
										variant="outline"
										onClick={handleStop}
										className="h-8 w-8 cursor-pointer border border-gray-800 rounded-full"
									>
										<StopCircle className="w-6 h-6" />
									</Button>
								) : (
									<Button
										type="submit"
										size="sm"
										disabled={!input.trim()}
										className="h-8 w-8 p-0 bg-black hover:bg-gray-800 cursor-pointer rounded-lg"
									>
										<Send className="w-4 h-4" />
									</Button>
								)}
							</div>
						</div>
					</form>
					<div className="text-xs text-gray-500 text-center mt-1">
						{selectedModel!.displayName} can make mistakes. Consider checking important information.
					</div>
				</div>
			</div>
		</SidebarInset>
	);
}
