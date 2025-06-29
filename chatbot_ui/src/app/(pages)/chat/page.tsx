"use client";

import { ChatMain } from "@/app/(pages)/chat/chat-main";
import { ChatSidebar } from "@/app/(pages)/chat/chat-sidebar";
import { LoadingCircle } from "@/components/ui/loading-circle";
import { SidebarProvider } from "@/components/ui/sidebar";
import { UserType } from "@/types/user.type";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function ChatPage() {
	const [user, setUser] = useState<UserType | null>(null);
	const [isLoading, setIsLoading] = useState(true);
	const router = useRouter();

	useEffect(() => {
		const userData = sessionStorage.getItem("user");

		if (!userData) {
			router.push("/");
			return;
		}

		setUser(JSON.parse(userData) as UserType);
		setIsLoading(false);
	}, []);

	if (isLoading) {
		return (
			<div className="flex h-screen w-full items-center justify-center">
				<LoadingCircle size="lg" />
			</div>
		);
	}

	return (
		<SidebarProvider>
			<div className="flex h-screen w-full">
				<ChatSidebar user={user!} />
				<ChatMain user={user!} />
			</div>
		</SidebarProvider>
	);
}
