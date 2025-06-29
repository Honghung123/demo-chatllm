"use client";

import GptSvg from "@/assets/svg/gpt.svg";
import { Button } from "@/components/ui/button";
import { MessageType } from "@/types/chat.type";
import { Check, Copy, RotateCcw, ThumbsDown, ThumbsUp } from "lucide-react";
import Image from "next/image";
import { useState } from "react";

interface ChatMessageProps {
	message: MessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
	const [copied, setCopied] = useState(false);

	const handleCopy = async () => {
		const doc = new DOMParser().parseFromString(message.content, "text/html");
		await navigator.clipboard.writeText(doc.body.textContent || "");
		setCopied(true);
		setTimeout(() => setCopied(false), 2000);
	};

	const formatContent = (content: string) => {
		// Simple formatting for line breaks
		return content.split("\n").map((line, index) => (
			<span key={index}>
				{line}
				{index < content.split("\n").length - 1 && <br />}
			</span>
		));
	};

	if (message.role === "user") {
		return (
			<div className="flex items-start space-x-4 justify-end">
				<div className="flex-1 max-w-2xl flex justify-end">
					<div className="bg-gray-100 rounded-lg p-2 ml-12">
						<span className="text-gray-900">{formatContent(message.content)}</span>
					</div>
				</div>
				<div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
					{message.role.charAt(0).toUpperCase()}
				</div>
			</div>
		);
	}

	return (
		<div className="flex items-start space-x-2 relative">
			<div className="p-0">
				<Image src={GptSvg} alt="GPT Logo" className="w-6 h-6" />
			</div>
			<div className="flex-1 group hover:bg-[#f5f5f5] px-2 rounded-md">
				<div className="prose prose-gray max-w-none">
					<div
						className={`${message.isError ? "text-red-500" : "text-gray-900"} leading-relaxed`}
						dangerouslySetInnerHTML={{ __html: message.content }}
					></div>
				</div>

				{/* Action buttons */}
				<div className="flex items-center space-x-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity absolute">
					{!message.isError && (
						<>
							<Button
								variant="ghost"
								size="sm"
								onClick={handleCopy}
								title="Copy"
								className="h-8 px-2 text-gray-500 hover:text-gray-700 cursor-pointer"
							>
								{copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
							</Button>
							<Button variant="ghost" size="sm" className="h-8 px-2 text-gray-500 hover:text-gray-700 cursor-pointer">
								<ThumbsUp className="w-4 h-4" />
							</Button>
							<Button variant="ghost" size="sm" className="h-8 px-2 text-gray-500 hover:text-gray-700 cursor-pointer">
								<ThumbsDown className="w-4 h-4" />
							</Button>
						</>
					)}
					<Button variant="ghost" size="sm" className="h-8 px-2 text-gray-500 hover:text-gray-700 cursor-pointer">
						<RotateCcw className="w-4 h-4" />
					</Button>
				</div>
			</div>
		</div>
	);
}
