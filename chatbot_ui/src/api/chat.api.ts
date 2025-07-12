import myAxios from "@/api/axios";
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
	const res = await myAxios.get<AIModel[]>(`/ai-models`, {
		headers: { "Content-Type": "application/json" },
	});
	return res.data;
};

export const getChatHistory = async (userId: string, chatId: string): Promise<MessageType[]> => {
	const res = await myAxios.get<MessageType[]>(`/chat-histories/${userId}/${chatId}`, {
		headers: { "Content-Type": "application/json" },
	});
	return res.data;
};

// CHAT_SIDEBAR
export const addNewCoversation = async (userId: string) => {
	const res = await myAxios.post<ConversationType>(`/conversations/new/${userId}`, {
		headers: { "Content-Type": "application/json" },
	});
	return res.data;
};

export const getAllChatHistories = async (userId: string) => {
	const res = await myAxios.get<ConversationType[]>(`/conversations/${userId}`, {
		headers: { "Content-Type": "application/json" },
	});
	return res.data;
};

export const getAllProvidedFiles = async (username: string) => {
	const res = await myAxios.get<FileListType[]>(`/files/${username}`, {
		headers: { "Content-Type": "application/json" },
	});
	res.data[0].icon = Settings;
	res.data[1].icon = User;
	return res.data;
};

export const uploadFileToServer = async (username: string, files: File[], roles: string[]) => {
	const formData = new FormData();
	for (let i = 0; i < files.length; i++) {
		formData.append("files", files[i]);
	}
	for (let i = 0; i < roles.length; i++) {
		formData.append("allowed_roles", roles[i]);
	}
	try {
		const res = await myAxios.post<FileType[]>(`/upload/${username}`, formData, {
			headers: {
				"Content-Type": "multipart/form-data",
			},
		});
		return res.data;
	} catch (error) {
		return [];
	}
};

export const deleteAllConversations = async () => {
	try {
		const res = await myAxios.get(`/clear-data`, {
			headers: { "Content-Type": "application/json" },
		});
		return res.status;
	} catch (error) {
		return 500;
	}
};
