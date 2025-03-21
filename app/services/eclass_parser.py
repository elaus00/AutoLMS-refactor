from bs4 import BeautifulSoup
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class EclassParser:
    """HTML 파싱 클래스"""

    def parse_courses(self, html: str) -> List[Dict[str, Any]]:
        """강의 목록 파싱"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            course_elements = soup.find_all('li', style=lambda value: value and 'background: url' in value)

            return [self._parse_course_element(element) for element in course_elements if self._parse_course_element(element)]
        except Exception as e:
            logger.error(f"강의 목록 파싱 중 오류 발생: {e}")
            return []

    def _parse_course_element(self, element) -> Optional[Dict[str, Any]]:
        """강의 요소 파싱"""
        try:
            name_elem = element.find('em', class_='sub_open')
            if not name_elem:
                return None

            course_id = name_elem.get('kj')
            full_name = name_elem.text.strip()
            name_parts = full_name.rsplit('(', 1)
            course_name = name_parts[0].strip()
            course_code = name_parts[1].strip(') ') if len(name_parts) > 1 else ''
            time_elem = element.find('span')
            course_time = time_elem.text.strip() if time_elem else ''

            return {
                'id': course_id,
                'name': course_name,
                'code': course_code,
                'time': course_time
            }
        except Exception as e:
            logger.error(f"강의 요소 파싱 중 오류 발생: {e}")
            return None

    def parse_course_menus(self, html: str) -> Dict[str, Dict[str, str]]:
        """강의 메뉴 파싱"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return self._get_specific_menus(soup)
        except Exception as e:
            logger.error(f"강의 메뉴 파싱 중 오류 발생: {e}")
            return {}

    def _get_specific_menus(self, soup: BeautifulSoup) -> Dict[str, Dict[str, str]]:
        """강의 메뉴 항목 파싱"""
        menus = {}
        menu_mapping = {
            'st_plan': 'plan',
            'st_onlineclass': 'online_lecture',
            'st_notice': 'notice',
            'st_lecture_material': 'lecture_material',
            'st_attendance': 'attendance',
            'st_report': 'assignment',
            'st_teamproject': 'team_project',
            'st_exam': 'exam'
        }

        menu_items = soup.find_all('li', class_='course_menu_item')
        for item in menu_items:
            menu_id = item.get('id', '')
            if menu_id in menu_mapping:
                link = item.find('a')
                if link:
                    menu_name = link.text.strip()
                    menu_url = link['href']
                    menus[menu_mapping[menu_id]] = {
                        'name': menu_name,
                        'url': menu_url
                    }
        return menus

    def parse_syllabus(self, html: str) -> Dict[str, Any]:
        """강의계획서 파싱"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return self._extract_syllabus_info(soup)
        except Exception as e:
            logger.error(f"강의계획서 파싱 중 오류 발생: {e}")
            return {}

    def _extract_syllabus_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """강의계획서 정보 추출"""
        syllabus_info = {
            '수업기본정보': {},
            '담당교수정보': {},
            '강의계획': {},
            '주별강의계획': []
        }

        sections = soup.find_all('div',
                                style=lambda value: value and 'padding-top' in value and 'font-weight: bold' in value)

        for section in sections:
            section_title = section.text.strip()
            section_key = None

            # 섹션 제목 맵핑
            if '[수업기본정보]' in section_title:
                section_key = '수업기본정보'
            elif '[담당교수정보]' in section_title:
                section_key = '담당교수정보'
            elif '[강의계획]' in section_title:
                section_key = '강의계획'
            elif '[주별강의계획]' in section_title:
                section_key = '주별강의계획'

            if section_key and section_key in syllabus_info:
                table = section.find_next('table')
                if table:
                    if section_key != '주별강의계획':
                        self._extract_table_info(table, syllabus_info[section_key])
                    else:
                        self._extract_weekly_syllabus(table, syllabus_info[section_key])

        return syllabus_info

    def _extract_table_info(self, table: BeautifulSoup, info_dict: Dict[str, str]) -> None:
        """테이블 정보 추출"""
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['th', 'td'])
            if len(cells) >= 2:
                key = cells[0].text.strip()
                value = cells[1].text.strip()
                info_dict[key] = value

    def _extract_weekly_syllabus(self, table: BeautifulSoup, weekly_syllabus: List[Dict[str, str]]) -> None:
        """주별 강의계획 추출"""
        rows = table.find_all('tr')[1:]  # 헤더 제외
        seen_weeks = set()  # 이미 처리한 주차 추적

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                week = cols[0].text.strip()
                content = cols[1].text.strip()
                note = cols[2].text.strip()

                # 빈 행이거나 이미 처리한 주차라면 건너뜀
                if not (week and content) or week in seen_weeks:
                    continue

                # 주차 기록
                seen_weeks.add(week)

                weekly_syllabus.append({
                    '주차': week,
                    '내용': content,
                    '비고': note
                })

    def parse_notice_list(self, html: str) -> List[Dict[str, Any]]:
        """공지사항 목록 파싱"""
        try:
            # 디버깅용 HTML 파일 저장
            # try:
            #     with open('debug_notice_list.html', 'w', encoding='utf-8') as f:
            #         f.write(html)
            #     logger.info("HTML 파일 저장 완료: debug_notice_list.html")
            # except Exception as e:
            #     logger.error(f"HTML 파일 저장 중 오류 발생: {e}")

            soup = BeautifulSoup(html, 'html.parser')
            logger.info("HTML 파싱 시작")

            notice_rows = soup.find_all('tr', style="cursor: pointer;")
            logger.info(f"발견된 공지사항 행 수: {len(notice_rows)}")

            if not notice_rows:
                logger.warning("공지사항 목록을 찾을 수 없습니다.")
                return []

            notices = []
            for row in notice_rows:
                try:
                    # onclick 속성에서 URL과 article_id 추출
                    onclick = row.select_one('td.left').get('onclick', '')
                    article_id = None
                    detail_url = ''

                    if onclick:
                        # pageMove 함수의 URL 파라미터 추출
                        url_match = re.search(r"pageMove\('([^']+)'\)", onclick)
                        if url_match:
                            detail_url = url_match.group(1)
                            # URL에서 ARTL_NUM 파라미터 추출
                            artl_match = re.search(r'ARTL_NUM=(\d+)', detail_url)
                            if artl_match:
                                article_id = artl_match.group(1)
                                detail_url = f"https://eclass.seoultech.ac.kr{detail_url}"

                    cols = row.find_all('td')
                    if len(cols) >= 5:
                        title_element = cols[2].find('div', class_='subjt_top')
                        title = title_element.get_text(strip=True) if title_element else ''

                        # 작성자 및 조회수 추출
                        bottom_div = cols[2].find('div', class_='subjt_bottom')
                        author = ''
                        views = ''

                        if bottom_div:
                            spans = bottom_div.find_all('span')
                            if spans:
                                author = spans[0].get_text(strip=True)
                                if len(spans) > 1:
                                    views_text = spans[-1].get_text(strip=True)
                                    views_match = re.search(r'\d+', views_text)
                                    if views_match:
                                        views = views_match.group()

                        notice = {
                            'number': cols[0].text.strip(),
                            'article_id': article_id,
                            'title': title,
                            'author': author,
                            'date': cols[4].text.strip(),
                            'views': int(views),
                            'url': detail_url
                        }
                        notices.append(notice)
                        # logger.info(f"파싱된 공지사항: {notice}")

                except Exception as e:
                    logger.error(f"공지사항 행 파싱 중 오류 발생: {e}")
                    continue

            # 최신순으로 정렬
            notices.reverse()
            return notices

        except Exception as e:
            logger.error(f"공지사항 목록 파싱 중 오류 발생: {e}")
            return []

    def _extract_url_from_onclick(self, onclick_value: str) -> str:
        """onclick 속성에서 URL 추출"""
        match = re.search(r"pageMove\('([^']+)'\)", onclick_value)
        if match:
            base_url = "https://eclass.seoultech.ac.kr"
            return base_url + match.group(1)
        return ""

    def _extract_article_id(self, url: str) -> Optional[str]:
        """URL에서 게시글 ID 추출"""
        if not url:
            return None

        # ARTL_NUM 또는 NORCT_NUM 파라미터 찾기
        for param in ['ARTL_NUM', 'NORCT_NUM']:
            match = re.search(fr'{param}=([\d]+)', url)
            if match:
                return match.group(1)

        return None


    def parse_notice_detail(self, html: str) -> Dict[str, Any]:
        """공지사항 상세 내용 파싱"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            detail = {}
            content_seq = None

            # URL에서 추출 시도
            url_match = re.search(r'CONTENT_SEQ=([^&]+)', html)
            if url_match:
                content_seq = url_match.group(1)
            # hidden input에서 추출 시도
            if not content_seq:
                seq_input = soup.select_one('input[name="CONTENT_SEQ"]')
                if seq_input:
                    content_seq = seq_input.get('value')

            # 텍스트뷰어 찾기
            textviewer = soup.find('td', class_='textviewer')
            if not textviewer:
                # 다른 방법으로 내용 찾기
                table = soup.find('table', class_='bbsview')
                if table:
                    rows = table.find_all('tr')
                    if rows and len(rows) > 0:
                        textviewer = rows[-1].find('td')

            if textviewer:
                # 내용 추출
                content_div = textviewer.find('div')
                if content_div:
                    # HTML 태그 처리
                    for br in content_div.find_all('br'):
                        br.replace_with('\n')
                    for p in content_div.find_all('p'):
                        p.insert_after(soup.new_string('\n'))
                    detail['content'] = content_div.get_text(strip=True)
                else:
                    # div가 없는 경우 직접 텍스트 추출
                    detail['content'] = textviewer.get_text(strip=True)

                # 첨부파일 추출
                attachments = self._extract_attachments(html, content_seq)
                if attachments:
                    detail['attachments'] = attachments

            return detail
        except Exception as e:
            logger.error(f"공지사항 상세 파싱 중 오류 발생: {e}")
            return {}

    def parse_material_list(self, html: str) -> List[Dict[str, Any]]:
        """강의자료 목록 파싱"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            material_rows = soup.select('tr[style*="cursor: pointer"]')

            if not material_rows:
                logger.warning("강의자료 목록을 찾을 수 없습니다.")
                return []

            materials = []
            for row in material_rows:
                try:
                    # 공지 글은 건너뛰기
                    if row.get('class') and any(cls in ['gongji', 'notitop'] for cls in row.get('class')):
                        continue

                    # 제목 열 찾기
                    title_cell = row.select_one('td.left')
                    if not title_cell:
                        continue

                    # URL 및 article_id 추출
                    onclick = title_cell.get('onclick', '')
                    detail_url = ''
                    article_id = None

                    if onclick:
                        # pageMove 함수의 URL 파라미터 추출 (event 파라미터가 있는 경우도 처리)
                        url_match = re.search(r"pageMove\('([^']+)'(?:,\s*event)?", onclick)
                        if url_match:
                            detail_url = url_match.group(1)
                            if not detail_url.startswith('http'):
                                detail_url = f"https://eclass.seoultech.ac.kr{detail_url}"
                            # URL에서 ARTL_NUM 파라미터 추출
                            artl_match = re.search(r'ARTL_NUM=(\d+)', detail_url)
                            if artl_match:
                                article_id = artl_match.group(1)

                    if not article_id or not detail_url:
                        logger.warning(f"URL 또는 article_id 추출 실패: {onclick}")
                        continue

                    # 제목 추출
                    title_div = title_cell.select_one('.subjt_top')
                    title = title_div.get_text(strip=True) if title_div else ""

                    # 작성자 추출
                    author = ""
                    subjt_bottom = title_cell.select_one('.subjt_bottom')
                    if subjt_bottom:
                        author_span = subjt_bottom.select_one('span')
                        if author_span:
                            author = author_span.get_text(strip=True)

                    # 날짜 추출
                    date_cell = row.select_one('td.number:last-child')
                    date = date_cell.get_text(strip=True) if date_cell else ""

                    # 첨부파일 아이콘 확인
                    download_icons = row.select('img.download_icon')
                    has_attachment = len(download_icons) > 0

                    material = {
                        'article_id': article_id,
                        'title': title,
                        'author': author,
                        'date': date,
                        'url': detail_url,
                        'has_attachment': has_attachment
                    }
                    materials.append(material)
                    logger.debug(f"파싱된 강의자료: {material}")

                except Exception as e:
                    logger.error(f"강의자료 행 파싱 중 오류: {str(e)}")
                    continue

            logger.info(f"파싱된 전체 강의자료 수: {len(materials)}")
            return materials

        except Exception as e:
            logger.error(f"강의자료 목록 파싱 중 오류 발생: {e}")
            return []

    async def parse_material_detail(self, http_session, html_content: str, course_id: str) -> Dict[str, Any]:
        """강의자료 상세 페이지 파싱

        Args:
            http_session: HTTP 클라이언트 세션 (aiohttp 또는 httpx 세션)
            html_content: 파싱할 HTML 내용
            course_id: 강좌 ID
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            parsed_data = {}

            # CONTENT_SEQ 추출
            content_seq = None
            for script in soup.find_all('script'):
                if script.string and 'CONTENT_SEQ' in script.string:
                    match = re.search(r'CONTENT_SEQ\s*:\s*["\']([^"\',]+)', script.string)
                    if match:
                        content_seq = match.group(1)
                        break

            # 본문 내용 추출
            content_element = soup.select_one('td.textviewer')
            if content_element:
                parsed_data['content'] = content_element.get_text(strip=True)
                parsed_data['content_html'] = str(content_element)

            # AJAX로 첨부파일 정보 요청
            if content_seq:
                efile_list_url = "https://eclass.seoultech.ac.kr/ilos/co/efile_list.acl"
                form_data = {
                    'ky': course_id,
                    'pf_st_flag': '2',  # 학생 권한
                    'CONTENT_SEQ': content_seq,
                    'encoding': 'utf-8'
                }

                try:
                    # http_session 사용 (EclassSession의 인스턴스)
                    file_list_response = await http_session.post(efile_list_url, data=form_data)

                    if file_list_response:
                        file_list_html = file_list_response.text

                        # 첨부파일 정보 추출
                        file_info_list = self._extract_attachments(file_list_html, content_seq)
                        if file_info_list:
                            parsed_data['attachments'] = file_info_list
                    else:
                        logger.error("첨부파일 목록 요청 실패")
                except Exception as e:
                    logger.error(f"첨부파일 AJAX 요청 중 오류: {str(e)}")

            return parsed_data

        except Exception as e:
            logger.error(f"강의자료 상세 정보 파싱 중 오류: {str(e)}")
            return {}

    def parse_assignment_list(self, html: str) -> List[Dict[str, Any]]:
        """과제 목록 파싱"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            # 과제 테이블 찾기
            assignment_table = soup.find('table', class_='table_topic')
            if not assignment_table:
                logger.warning("과제 테이블을 찾을 수 없습니다.")
                return []

            # 과제 행 찾기
            assignment_rows = assignment_table.find_all('tr')[1:]  # 헤더 제외

            assignments = []
            for row in assignment_rows:
                cols = row.find_all('td')
                if len(cols) < 7:  # 과제 행은 보통 7개 이상의 열을 가짐
                    continue

                # onclick 속성에서 URL 추출
                onclick_value = row.get('onclick', '')
                detail_url = self._extract_url_from_onclick(onclick_value)

                # 과제 ID 추출
                assignment_id = self._extract_article_id(detail_url)

                assignment = {
                    'assignment_id': assignment_id,
                    'title': cols[1].text.strip(),
                    'start_date': cols[3].text.strip(),
                    'end_date': cols[4].text.strip(),
                    'status': cols[5].text.strip(),
                    'url': detail_url
                }
                assignments.append(assignment)

            return assignments
        except Exception as e:
            logger.error(f"과제 목록 파싱 중 오류 발생: {e}")
            return []

    def parse_assignment_detail(self, html: str) -> Dict[str, Any]:
        """과제 상세 내용 파싱"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            detail = {}

            # 과제 테이블 찾기
            assignment_table = soup.find('table', class_='bbsview')
            if assignment_table:
                # 과제 내용 추출
                content_td = assignment_table.find('td', class_='textviewer')
                if content_td:
                    # HTML 태그 처리
                    for br in content_td.find_all('br'):
                        br.replace_with('\n')
                    for p in content_td.find_all('p'):
                        p.insert_after(soup.new_string('\n'))

                    detail['content'] = content_td.get_text(strip=True)

                # 첨부파일 추출
                attachments = self._extract_attachments(soup)
                if attachments:
                    detail['attachments'] = attachments

            return detail
        except Exception as e:
            logger.error(f"과제 상세 파싱 중 오류 발생: {e}")
            return {}

    def _extract_attachments(self, html_content: str, content_seq: str) -> List[Dict[str, Any]]:
        """첨부파일 정보 추출"""
        attachments = []
        soup = BeautifulSoup(html_content, 'html.parser')

        for file_link in soup.find_all('a', href=lambda h: h and 'efile_download.acl' in h):
            try:
                file_url = file_link.get('href', '')
                file_name = file_link.text.strip()

                # FILE_SEQ 추출
                file_seq_match = re.search(r'FILE_SEQ=([^&]+)', file_url)
                if not file_seq_match:
                    continue

                file_seq = file_seq_match.group(1)

                attachment = {
                    'name': file_name,
                    'url': file_url if file_url.startswith('http') else f"https://eclass.seoultech.ac.kr{file_url}",
                    'file_seq': file_seq,
                    'content_seq': content_seq
                }
                attachments.append(attachment)
                logger.debug(f"첨부파일 정보 추출: {attachment}")

            except Exception as e:
                logger.error(f"첨부파일 정보 추출 중 오류: {str(e)}")
                continue

        return attachments