"use client";

import type React from "react";

import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { useState, useRef, useEffect } from "react";
import { Upload, X, File, ImageIcon, FileText, Download, LoaderCircle } from "lucide-react";
import eventBus from "@/hooks/event-bus";

interface UploadedFile {
	file: File;
	preview?: string;
	id: string;
}

export default function UploadFileModal({ children }: { children: React.ReactNode }) {
	const [open, setOpen] = useState(false);
	const [isProcessingUpload, setIsProcessingUpload] = useState(false);
	const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
	const fileInputRef = useRef<HTMLInputElement>(null);

	const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
		const files = Array.from(event.target.files || []);

		files.forEach((file) => {
			const fileId = Date.now().toString() + Math.random().toString(36).substr(2, 9);
			const uploadedFile: UploadedFile = {
				file,
				id: fileId,
			};

			// Create preview for images
			if (file.type.startsWith("image/")) {
				const reader = new FileReader();
				reader.onload = (e) => {
					setUploadedFiles((prev) =>
						prev.map((f) => (f.id === fileId ? { ...f, preview: e.target?.result as string } : f))
					);
				};
				reader.readAsDataURL(file);
			}

			setUploadedFiles((prev) => [...prev, uploadedFile]);
		});

		// Reset input
		if (fileInputRef.current) {
			fileInputRef.current.value = "";
		}
	};

	const handleFileButtonClick = () => {
		fileInputRef.current?.click();
	};

	const removeFile = (fileId: string) => {
		setUploadedFiles((prev) => prev.filter((f) => f.id !== fileId));
	};

	const handleUpload = () => {
		setIsProcessingUpload(true);
		eventBus.emit("uploadFiles", { files: uploadedFiles.map((f) => f.file) });
	};

	useEffect(() => {
		const unsubscribe = eventBus.on("confirmUploadFiles", async (payload) => {
			setIsProcessingUpload(false);
			if (payload.result) {
				setUploadedFiles([]);
				setOpen(false);
			} else {
				alert("Upload failed: " + payload.error?.message);
			}
		});
		return () => {
			unsubscribe();
		};
	}, []);

	const getFileIcon = (fileType: string) => {
		if (fileType.startsWith("image/")) return <ImageIcon className="w-4 h-4" />;
		if (fileType.includes("pdf")) return <FileText className="w-4 h-4" />;
		return <File className="w-4 h-4" />;
	};

	const formatFileSize = (bytes: number) => {
		if (bytes === 0) return "0 Bytes";
		const k = 1024;
		const sizes = ["Bytes", "KB", "MB", "GB"];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
	};

	return (
		<Popover open={open} onOpenChange={setOpen}>
			<PopoverTrigger asChild>{children}</PopoverTrigger>
			<PopoverContent className="w-96 border border-gray-200 !p-0" align="center">
				<div className="p-4">
					<div className="flex items-center justify-between mb-4">
						<h3 className="text-lg font-semibold">Upload Files</h3>
						<Button variant="ghost" size="sm" onClick={() => setOpen(false)} className="h-6 w-6 p-0">
							<X className="w-4 h-4" />
						</Button>
					</div>

					{/* File Upload Area */}
					<div className="space-y-4">
						<input
							ref={fileInputRef}
							type="file"
							multiple
							onChange={handleFileUpload}
							className="hidden"
							accept=".pdf,.doc,.docx,.txt,.xlsx,.csv,.pptx"
						/>

						<Button
							onClick={handleFileButtonClick}
							variant="outline"
							className="w-full h-24 border-2 border-dashed border-gray-300 hover:border-gray-400 flex flex-col items-center justify-center gap-2 bg-transparent"
						>
							<Upload className="w-6 h-6 text-gray-500" />
							<span className="text-sm text-gray-600">Click to upload files</span>
							<span className="text-xs text-gray-400">Support: PPTX, PDF, DOC, TXT, etc.</span>
						</Button>

						{uploadedFiles.length > 0 && (
							<div className="space-y-2 max-h-64 overflow-y-auto">
								<h4 className="text-sm font-medium text-gray-700">Uploaded Files ({uploadedFiles.length})</h4>
								{uploadedFiles.map((uploadedFile) => (
									<div key={uploadedFile.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg border">
										{/* File Preview or Icon */}
										<div className="flex-shrink-0">
											{uploadedFile.preview ? (
												<img
													src={uploadedFile.preview || "/placeholder.svg"}
													alt={uploadedFile.file.name}
													className="w-10 h-10 object-cover rounded"
												/>
											) : (
												<div className="w-10 h-10 bg-gray-200 rounded flex items-center justify-center">
													{getFileIcon(uploadedFile.file.type)}
												</div>
											)}
										</div>

										<div className="flex-1 min-w-0">
											<p className="text-sm font-medium text-gray-900 truncate">{uploadedFile.file.name}</p>
											<p className="text-xs text-gray-500">{formatFileSize(uploadedFile.file.size)}</p>
										</div>

										<Button
											onClick={() => removeFile(uploadedFile.id)}
											variant="ghost"
											size="sm"
											className="h-6 w-6 p-0 text-gray-400 hover:text-red-500"
										>
											<X className="w-4 h-4" />
										</Button>
									</div>
								))}
							</div>
						)}

						{uploadedFiles.length > 0 && (
							<div className="flex space-x-2 pt-4 border-t">
								{isProcessingUpload ? (
									<>
										<Button disabled className="flex-1 cursor-pointer bg-black text-white">
											<LoaderCircle className="w-4 h-4 mr-2 animate-spin" stroke="white" />
											Uploading...
										</Button>
									</>
								) : (
									<>
										<Button onClick={handleUpload} className="flex-1 cursor-pointer bg-black text-white">
											<Upload className="w-4 h-4 mr-2" />
											Upload ({uploadedFiles.length})
										</Button>
									</>
								)}
								<Button onClick={() => setUploadedFiles([])} variant="outline" className="px-4 cursor-pointer">
									Clear All
								</Button>
							</div>
						)}
					</div>
				</div>
			</PopoverContent>
		</Popover>
	);
}
