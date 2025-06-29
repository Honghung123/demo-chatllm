import { AIModel, ChatRequestType, ConversationType, FileListType, FileType, MessageType } from "@/types/chat.type";
import axios from "axios";
import { Settings, User } from "lucide-react";

const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;

export const chatStreamingResponse = async (request: ChatRequestType, controller: AbortController) => {
	const res = await fetch(`${BASE_URL}/chat`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(request),
		signal: controller.signal,
	});

	return res;
};

export const getAllAiModels = async () => {
	const res = await axios.get<AIModel[]>(`${BASE_URL}/ai-models`, {
		headers: { "Content-Type": "application/json" },
	});
	return res.data;
};

export const getChatHistory = async (userId: string, chatId: string): Promise<MessageType[]> => {
	const res = await axios.get<MessageType[]>(`${BASE_URL}/chat-histories/${userId}/${chatId}`, {
		headers: { "Content-Type": "application/json" },
	});
	return res.data;
};

// CHAT_SIDEBAR
export const addNewCoversation = async (userId: string) => {
	const res = await axios.post<ConversationType>(`${BASE_URL}/new-conversation/${userId}`, {
		headers: { "Content-Type": "application/json" },
	});
	return res.data;
};

export const getAllChatHistories = async (userId: string) => {
	const res = await axios.get<ConversationType[]>(`${BASE_URL}/chat-histories/${userId}`, {
		headers: { "Content-Type": "application/json" },
	});
	return res.data;
};

export const getAllProvidedFiles = async (userId: string) => {
	const res = await axios.get<FileListType[]>(`${BASE_URL}/files/${userId}`, {
		headers: { "Content-Type": "application/json" },
	});
	res.data[0].icon = Settings;
	res.data[1].icon = User;
	return res.data;
};

export const uploadFileToServer = async (userId: string, files: File[]) => {
	const formData = new FormData();
	for (let i = 0; i < files.length; i++) {
		formData.append("files", files[i]);
	}
	try {
		const res = await axios.post<FileType[]>(`${BASE_URL}/upload/${userId}`, formData, {
			headers: {
				"Content-Type": "multipart/form-data",
			},
		});
		return res.data;
	} catch (error) {
		return [];
	}
};
