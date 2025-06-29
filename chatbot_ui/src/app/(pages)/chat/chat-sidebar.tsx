"use client";

import { addNewCoversation, getAllChatHistories, getAllProvidedFiles, uploadFileToServer } from "@/api/chat.api";
import { getFileIcon } from "@/app/(pages)/chat/files";
import GptSvg from "@/assets/svg/gpt.svg";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
	Sidebar,
	SidebarContent,
	SidebarGroup,
	SidebarGroupContent,
	SidebarGroupLabel,
	SidebarHeader,
	SidebarMenu,
	SidebarMenuAction,
	SidebarMenuButton,
	SidebarMenuItem,
	SidebarMenuSub,
} from "@/components/ui/sidebar";
import eventBus from "@/hooks/event-bus";
import { ConversationType, FileListType } from "@/types/chat.type";
import { UserType } from "@/types/user.type";
import { ChevronRight, Edit3, MoreHorizontal, PlusIcon, Trash2 } from "lucide-react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

interface ChatSidebarProps {
	user: UserType;
}

export function ChatSidebar({ user }: ChatSidebarProps) {
	const [chatHistory, setChatHistory] = useState<ConversationType[]>([]);
	const [listFiles, setListFiles] = useState<FileListType[]>([]);
	const [selectedChat, setSelectedChat] = useState("1");
	const listFilesRef = useRef(listFiles);

	// Đồng bộ ref mỗi khi state thay đổi
	useEffect(() => {
		listFilesRef.current = listFiles;
	}, [listFiles]);

	useEffect(() => {
		const fetchData = async () => {
			const [chatHistoriesList, listProvidedFiles] = await Promise.all([
				getAllChatHistories(user.id.toString()),
				getAllProvidedFiles(user.id.toString()),
			]);
			setChatHistory(chatHistoriesList);
			setListFiles(listProvidedFiles);
		};
		fetchData();
	}, []);

	useEffect(() => {
		const unsubscribe = eventBus.on("uploadFiles", async (payload) => {
			try {
				const files = payload.files;
				const response = await uploadFileToServer(user.id.toString(), files);
				const existingFiles = [...listFilesRef.current];
				existingFiles[1].listFiles.push(...response);
				setListFiles(existingFiles);
				listFilesRef.current = existingFiles;
				eventBus.emit("confirmUploadFiles", { result: true });
			} catch (error: any) {
				eventBus.emit("confirmUploadFiles", { result: false, error: error });
			}
		});
		return () => {
			unsubscribe();
		};
	}, []);

	const handleAddNewChat = async () => {
		const newChatConversation = await addNewCoversation(user.id.toString());
		setChatHistory([newChatConversation, ...chatHistory]);
		eventBus.emit("changeConversation", { chatId: newChatConversation.chatId });
		setSelectedChat(newChatConversation.chatId);
	};

	const handleSelectChat = (chatId: string) => {
		eventBus.emit("changeConversation", { chatId: chatId });
		setSelectedChat(chatId);
	};

	const handleDeleteChat = (chatId: string) => {
		setChatHistory((prev) => prev.filter((chat) => chat.chatId !== chatId));
	};

	return (
		<Sidebar className="border-r border-gray-200 bg-sidebar select-none">
			<SidebarHeader className="p-2">
				<div className="flex items-center justify-between">
					<div className="flex items-center justify-center">
						<Image src={GptSvg} alt="GPT Logo" className="w-8 h-8" />
					</div>
				</div>

				<SidebarMenu>
					<SidebarMenuItem>
						<SidebarMenuButton
							className="w-full cursor-pointer justify-start text-gray-700 hover:bg-[#efefef]"
							onClick={() => handleAddNewChat()}
						>
							<PlusIcon className="w-4 h-4 mr-3" />
							New chat
						</SidebarMenuButton>
					</SidebarMenuItem>
				</SidebarMenu>
			</SidebarHeader>

			<SidebarContent>
				<SidebarGroup>
					<SidebarGroupLabel className="text-gray-500 text-sm font-medium p-2">Chats</SidebarGroupLabel>
					<SidebarGroupContent>
						<ScrollArea className="max-h-[11rem] overflow-auto">
							<SidebarMenu>
								{chatHistory.map((chat, index) => (
									<SidebarMenuItem key={index}>
										<SidebarMenuButton
											isActive={selectedChat == chat.chatId}
											onClick={() => handleSelectChat(chat.chatId)}
											className="w-full justify-start text-gray-700 hover:bg-[#efefef] data-[active=true]:bg-[#efefef] cursor-pointer"
										>
											<span className="truncate">{chat.title}</span>
										</SidebarMenuButton>
										<DropdownMenu>
											<DropdownMenuTrigger asChild>
												<SidebarMenuAction className="opacity-0 group-hover:opacity-100 cursor-pointer">
													<MoreHorizontal className="w-4 h-4" />
												</SidebarMenuAction>
											</DropdownMenuTrigger>
											<DropdownMenuContent align="end" className="w-48">
												{/* <DropdownMenuItem>
													<Share className="w-4 h-4 mr-2" />
													Share
												</DropdownMenuItem> */}
												<DropdownMenuItem>
													<Edit3 className="w-4 h-4 mr-2" />
													Rename
												</DropdownMenuItem>
												{/* <DropdownMenuItem>
													<Archive className="w-4 h-4 mr-2" />
													Archive
												</DropdownMenuItem> */}
												<DropdownMenuItem className="text-red-600" onClick={() => handleDeleteChat(chat.chatId)}>
													<Trash2 className="w-4 h-4 mr-2" />
													Delete
												</DropdownMenuItem>
											</DropdownMenuContent>
										</DropdownMenu>
									</SidebarMenuItem>
								))}
							</SidebarMenu>
						</ScrollArea>
					</SidebarGroupContent>
				</SidebarGroup>
				<SidebarGroup>
					<SidebarGroupLabel className="text-gray-500 text-sm font-medium p-2">Files</SidebarGroupLabel>
					<SidebarGroupContent>
						<ScrollArea className="max-h-[15rem]">
							<SidebarMenu>
								{listFiles.map((listFile, index) => (
									<Collapsible key={index} asChild defaultOpen={true} className="group/collapsible">
										<SidebarMenuItem key={index}>
											<CollapsibleTrigger asChild>
												<SidebarMenuButton className="!p-1 cursor-pointer !hover:bg-[#efefef]">
													<listFile.icon />
													<span>{listFile.name}</span>
													<ChevronRight className="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
												</SidebarMenuButton>
											</CollapsibleTrigger>
											<CollapsibleContent className="max-h-[12rem]">
												{listFile.listFiles.map((file, index) => (
													<SidebarMenuSub key={index} className="!p-0 !mr-0">
														<SidebarMenuButton className="w-full justify-start text-gray-700 hover:bg-[#efefef] data-[active=true]:bg-[#efefef] cursor-pointer !p-1">
															<div className="flex gap-1">
																<Image src={getFileIcon(file.extension)} alt="File Icon" className="w-4 h-4" />
																<span className="truncate line-clamp-1">{file.fileName}</span>
															</div>
														</SidebarMenuButton>
														<DropdownMenu>
															<DropdownMenuTrigger asChild>
																<SidebarMenuAction className="opacity-0 group-hover:opacity-100 cursor-pointer">
																	<MoreHorizontal className="w-4 h-4" />
																</SidebarMenuAction>
															</DropdownMenuTrigger>
															<DropdownMenuContent align="end" className="w-48">
																<DropdownMenuItem>
																	<Edit3 className="w-4 h-4 mr-2" />
																	Rename
																</DropdownMenuItem>
																<DropdownMenuItem className="text-red-600" onClick={() => {}}>
																	<Trash2 className="w-4 h-4 mr-2" />
																	Delete
																</DropdownMenuItem>
															</DropdownMenuContent>
														</DropdownMenu>
													</SidebarMenuSub>
												))}
											</CollapsibleContent>
										</SidebarMenuItem>
									</Collapsible>
								))}
							</SidebarMenu>
						</ScrollArea>
					</SidebarGroupContent>
				</SidebarGroup>
			</SidebarContent>
		</Sidebar>
	);
}
