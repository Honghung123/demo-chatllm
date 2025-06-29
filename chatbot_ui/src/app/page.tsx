"use client";

import { LoadingCircle } from "@/components/ui/loading-circle";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function ChatPage() {
	const router = useRouter();

	useEffect(() => {
		// Check if user is authenticated
		const userData = sessionStorage.getItem("user");

		if (!userData) {
			router.push("/login");
			return;
		} else {
			router.push("/chat");
		}
	}, []);

	return (
		<div className="min-h-screen bg-white flex items-center justify-center">
			<LoadingCircle size="lg" />
		</div>
	);
}
