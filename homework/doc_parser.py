import fitz  
from typing import List, Dict

def is_in_header_footer(bbox: fitz.Rect, page_height: float, header_frac: float = 0.05, footer_frac: float = 0.08) -> bool:
    """
    페이지의 헤더 또는 푸터 영역에 속하는지 확인합니다.
    제목이 헤더로 오인되지 않도록 상단 영역(header_frac)을 보수적으로 설정합니다.
    """
    top_cut = page_height * header_frac
    bottom_cut = page_height * (1 - footer_frac)

    if bbox.y0 < top_cut:
        return True
    if bbox.y1 > bottom_cut:
        return True
    return False

def extract_structured_chunks(pdf_path: str) -> List[Dict]:
    """
    PDF에서 페이지별로 제목과 본문 덩어리(chunk)를 구조적으로 추출합니다.

    주요 로직:
    1. get_text("dict")를 사용해 텍스트 블록과 함께 폰트 크기 등 상세 정보를 가져옵니다.
    2. 헤더/푸터 및 노이즈(짧은 텍스트, 이미지 캡션 등)를 제거합니다.
    3. 블록 간의 수직 간격, 폰트 크기, 수평 정렬을 기반으로 연관된 블록들을 하나의 문단(chunk)으로 그룹화합니다.
    4. 페이지 상단에서 가장 큰 폰트를 가진 텍스트를 페이지의 제목으로 식별합니다.
    """
    doc = fitz.open(pdf_path)
    result = []
    
    for page_idx, page in enumerate(doc):
        page_height = page.rect.height
        
        # 1. get_text("dict")로 상세 정보가 포함된 블록 추출 및 필터링
        page_dict = page.get_text("dict", sort=True)
        raw_blocks = [b for b in page_dict.get("blocks", []) if b.get('type') == 0]

        text_blocks = []
        for block in raw_blocks:
            bbox = fitz.Rect(block['bbox'])
            # 헤더/푸터 영역 블록은 건너뜁니다.
            if is_in_header_footer(bbox, page_height):
                continue
            
            block_text = ""
            sizes = []
            spans = [span for line in block.get('lines', []) for span in line.get('spans', [])]
            if not spans:
                continue

            # 블록 내 모든 텍스트를 합치고 평균 폰트 크기를 계산합니다.
            for span in spans:
                block_text += span.get('text', '')
                sizes.append(span.get('size', 0))
            
            block_text = block_text.strip()
            # 의미 없는 짧은 텍스트, 이미지 캡션 등을 필터링합니다.
            if not block_text or "OCN" in block_text or "본 도안은" in block_text or len(block_text) < 2:
                continue
            
            avg_size = sum(sizes) / len(sizes) if sizes else 0
            text_blocks.append({'bbox': bbox, 'text': block_text, 'size': avg_size})

        if not text_blocks:
            result.append({"page": page_idx + 1, "title": None, "chunks": []})
            continue

        # 2. 필터링된 블록들을 의미 단위(문단)로 그룹핑
        grouped_chunks = []
        if text_blocks:
            current_chunk = [text_blocks[0]]
            for i in range(1, len(text_blocks)):
                prev_block = current_chunk[-1]
                current_block = text_blocks[i]
                
                # 블록을 합칠지 여부를 결정하는 조건
                vertical_gap = current_block['bbox'].y0 - prev_block['bbox'].y1
                is_vertically_close = 0 <= vertical_gap < prev_block['size'] * 0.75
                is_font_similar = abs(current_block['size'] - prev_block['size']) < 1.0
                is_horizontally_aligned = abs(current_block['bbox'].x0 - prev_block['bbox'].x0) < 20

                # 폰트가 갑자기 커지거나 수직 간격이 크면 새로운 문단으로 판단
                starts_new_section = vertical_gap > prev_block['size'] * 1.5 or current_block['size'] > prev_block['size'] * 1.15
                
                if is_vertically_close and is_font_similar and is_horizontally_aligned and not starts_new_section:
                    current_chunk.append(current_block) # 현재 문단에 추가
                else:
                    grouped_chunks.append(current_chunk) # 현재 문단을 저장하고
                    current_chunk = [current_block]      # 새로운 문단 시작

            grouped_chunks.append(current_chunk) # 마지막 문단 추가

        final_chunks = ["\n".join([block['text'] for block in group]) for group in grouped_chunks]
        
        # 3. 페이지 제목 찾기
        page_title = None
        
        # 페이지 상단 20% 영역에서 가장 폰트가 큰 덩어리를 제목으로 간주
        potential_titles = [(g, g[0]['size']) for g in grouped_chunks if g[0]['bbox'].y0 < page_height * 0.20]
        if potential_titles:
            potential_titles.sort(key=lambda x: x[1], reverse=True)
            title_group = potential_titles[0][0]
            title_text = "\n".join([block['text'] for block in title_group])

            # 해당 덩어리가 chunk 리스트에 있으면 제목으로 설정하고 리스트에서 제거
            if title_text in final_chunks:
                page_title = title_text
                final_chunks.remove(title_text)

        result.append({
            "page": page_idx + 1,
            "title": page_title,
            "chunks": [c.strip() for c in final_chunks if c.strip()]
        })
        
    doc.close()
    return result