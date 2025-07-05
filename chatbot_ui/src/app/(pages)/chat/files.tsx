import ExcelSvg from "@/assets/svg/excel.svg";
import DocxSvg from "@/assets/svg/docx.svg";
import PdfSvg from "@/assets/svg/pdf.svg";
import PptxSvg from "@/assets/svg/pptx.svg";
import TxtSvg from "@/assets/svg/txt.svg";

export function getFileIcon(extension: string) {
	switch (extension) {
		case "docx":
			return DocxSvg;
		case "pdf":
			return PdfSvg;
		case "xlsx":
		case "csv":
			return ExcelSvg;
		case "pptx":
			return PptxSvg;
		case "excel":
			return ExcelSvg;
		default:
			return TxtSvg;
	}
}
