from typing import List, Dict, Any
import re
from bs4 import BeautifulSoup
import logging
from app.services.parsers.content_parser import ContentParser

logger = logging.getLogger(__name__)

class CourseParser(ContentParser):
    """강의 정보 파싱 클래스"""
    
    def parse_list(self, html: str) -> List[Dict[str, Any]]:
        """강의 목록 페이지 파싱"""
        try:
            if not html:
                return []
                
            soup = BeautifulSoup(html, 'html.parser')
            course_elements = soup.find_all('li', style=lambda value: value and 'background: url' in value)
            
            courses = []
            for element in course_elements:
                try:
                    # 강의명 요소 찾기
                    name_elem = element.find('em', class_='sub_open')
                    if not name_elem:
                        continue
                        
                    # 강의 ID 추출
                    course_id = name_elem.get('kj')
                    full_name = name_elem.text.strip()
                    
                    # 강의명과 코드 분리
                    name_parts = full_name.rsplit('(', 1)
                    course_name = name_parts[0].strip()
                    course_code = name_parts[1].strip(') ') if len(name_parts) > 1 else ''
                    
                    # 강의 시간 추출
                    time_elem = element.find('span')
                    course_time = time_elem.text.strip() if time_elem else ''
                    
                    # 결과 추가
                    if course_id and course_name:
                        courses.append({
                            'id': course_id,
                            'name': course_name,
                            'code': course_code,
                            'time': course_time
                        })
                except Exception as e:
                    logger.error(f"강의 요소 파싱 중 오류 발생: {e}")
                    continue
                    
            return courses
            
        except Exception as e:
            logger.error(f"강의 목록 파싱 중 오류 발생: {e}")
            return []
    
    def parse_detail(self, html: str) -> Dict[str, Any]:
        """
        강의 상세 페이지 파싱 (메뉴 정보)
        
        Note:
            강의는 상세 페이지가 없으므로 메뉴 정보를 파싱합니다.
        """
        return {'menus': self.parse_course_menus(html)}
    
    def parse_course_menus(self, html: str) -> Dict[str, Dict[str, str]]:
        """강의 메뉴 파싱"""
        try:
            if not html:
                return {}
                
            soup = BeautifulSoup(html, 'html.parser')
            menus = {}
            
            # 메뉴 매핑 정의
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
            
            # 메뉴 항목 찾기
            menu_items = soup.find_all('li', class_='course_menu_item')
            
            for item in menu_items:
                try:
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
                except Exception as e:
                    logger.error(f"메뉴 항목 파싱 중 오류: {str(e)}")
                    continue
                    
            return menus
            
        except Exception as e:
            logger.error(f"강의 메뉴 파싱 중 오류 발생: {e}")
            return {}
            
    async def parse_detail_with_attachments(self, eclass_session, html: str, course_id: str) -> Dict[str, Any]:
        """
        첨부파일 정보를 포함한 강의 상세 페이지 파싱
        (강의에는 첨부파일이 없으므로 기본 parse_detail을 사용)
        """
        return self.parse_detail(html)
