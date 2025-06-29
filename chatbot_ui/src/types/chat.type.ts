import { LucideIcon } from "lucide-react";

export type ConversationType = {
	chatId: string;
	userId: string;
	title: string;
	createdAt: string;
};

export type ChatMessageHistoryType = {
	role: "user" | "assistant";
	content: string;
};

export type AIModel = {
	model: string;
	modelName: string;
	displayName: string;
	description: string;
};

export type ChatRequestType = {
	role: string;
	content: string;
	history: ChatMessageHistoryType[];
	model: string;
	modelName: string;
};

export type ChatResponseType = {
	id: string;
	role: "assistant";
	content: string;
	timestamp: string;
};

export type MessageType = {
	id: string;
	role: "user" | "assistant";
	content: string;
	timestamp: string;
	isError?: boolean;
};

export type FileListType = {
	icon: LucideIcon;
	name: string;
	listFiles: FileType[];
};

export type FileType = {
	id: string;
	userId: string;
	name: string;
	fileName: string;
	fileNameInServer: string;
	extension: string;
	timestamp: string;
};
