import { LucideIcon } from "lucide-react";

export type ConversationType = {
	id: string;
	user_id: string;
	title: string;
	timestamp: string;
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
	userId: string;
	username: string;
	userRole: string;
	conversationId: string;
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
	message_id: string;
	conversation_id: string;
	user_id: string;
	content: string;
	from_user: boolean;
	timestamp: string;
	is_error?: boolean;
};

export type FileListType = {
	icon: LucideIcon;
	name: string;
	listFiles: FileType[];
};

export type FileType = {
	id: string;
	name: string;
	orginal_name: string;
	username: string;
	extension: string;
	timestamp: string;
};
