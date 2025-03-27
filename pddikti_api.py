import aiohttp
import json
import asyncio
import logging
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

async def login_pddikti(session):
    """Login ke PDDikti dan dapatkan token"""
    try:
        logger.info("Starting PDDikti login process")
        # STEP 1: GET /signin
        await session.get(
            "https://pddikti-admin.kemdikbud.go.id/signin",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30
        )
        
        # STEP 2: POST /login/login
        login_data = {
            'data[username]': 'MDQzMTc2',
            'data[password]': 'QEA8PkxrajEyMg==',
            'data[issso]': 'false'
        }
        login_response = await session.post(
            "https://api-pddikti-admin.kemdikbud.go.id/login/login",
            data=login_data,
            headers={
                "Origin": "https://pddikti-admin.kemdikbud.go.id",
                "Referer": "https://pddikti-admin.kemdikbud.go.id/",
                "User-Agent": "Mozilla/5.0"
            },
            timeout=30
        )
        
        if login_response.status == 200:
            data = await login_response.json()
            i_iduser = data["result"]["session_data"]["i_iduser"]
            id_organisasi = data["result"]["session_data"]["i_idunit"]
            logger.info(f"Login step 1-2 successful, got user ID: {i_iduser}")
            
            # STEP 3: GET /isverified
            await session.get(
                f"https://api-pddikti-admin.kemdikbud.go.id/isverified/{i_iduser}",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=30
            )
            
            # STEP 4: POST /login/roles/1?login=adm
            await session.post(
                "https://api-pddikti-admin.kemdikbud.go.id/login/roles/1?login=adm",
                data={'data[i_iduser]': i_iduser},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=30
            )
            
            # STEP 5: POST /login/setlogin/3/{id_organisasi}
            setlogin_data = {
                'data[i_username]': '043176',
                'data[i_iduser]': i_iduser,
                'data[password]': '@@<>Lkj122',
                'data[is_manual]': 'true'
            }
            setlogin_response = await session.post(
                f"https://api-pddikti-admin.kemdikbud.go.id/login/setlogin/3/{id_organisasi}?id_pengguna={i_iduser}&id_unit={id_organisasi}&id_role=3",
                data=setlogin_data,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=30
            )
            
            if setlogin_response.status == 200:
                setlogin_result = await setlogin_response.json()
                pm_token = setlogin_result["result"]["session_data"]["pm"]
                logger.info("Login to PDDikti completed successfully")
                return i_iduser, id_organisasi, pm_token
            else:
                logger.error(f"Setlogin failed with status: {setlogin_response.status}")
        else:
            logger.error(f"Login failed with status: {login_response.status}")
        
        logger.error("Login failed")
        return None, None, None
                
    except asyncio.TimeoutError:
        logger.error("Timeout during login to PDDikti")
        return None, None, None
    except aiohttp.ClientError as e:
        logger.error(f"Network error during login: {str(e)}")
        return None, None, None
    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        return None, None, None

async def search_student(keyword, i_iduser, pm_token, session):
    """Cari data mahasiswa"""
    try:
        logger.info(f"Searching for student with keyword: {keyword}")
        # Cari mahasiswa
        search_data = {
            'data[keyword]': keyword,
            'data[id_sp]': '',
            'data[id_sms]': '',
            'data[vld]': '0'
        }
        
        search_url = f"https://api-pddikti-admin.kemdikbud.go.id/mahasiswa/result?limit=20&page=0&id_pengguna={i_iduser}&id_role=3&pm={pm_token}"
        logger.info(f"Sending search request to PDDikti API")
        
        # Use a longer timeout for search
        try:
            response = await asyncio.wait_for(
                session.post(search_url, data=search_data, headers={"User-Agent": "Mozilla/5.0"}),
                timeout=60.0
            )
            
            if response.status == 200:
                logger.info("Search request successful, parsing results")
                data = await response.json()
                results = data.get("result", {}).get("data", [])
                logger.info(f"Found {len(results)} results for keyword '{keyword}'")
                return results
            else:
                logger.error(f"Search failed with status {response.status}")
                try:
                    error_text = await response.text()
                    logger.error(f"Error response: {error_text[:200]}")
                except:
                    pass
                return []
        except asyncio.TimeoutError:
            logger.error(f"Timeout during search operation for keyword '{keyword}'")
            return []
                
    except aiohttp.ClientError as e:
        logger.error(f"Network error during search: {str(e)}")
        return []
    except asyncio.TimeoutError:
        logger.error(f"Timeout during search for keyword '{keyword}'")
        return []
    except Exception as e:
        logger.error(f"Error during search: {str(e)}", exc_info=True)
        return []

async def get_student_detail(id_reg_pd, i_iduser, id_organisasi, pm_token, session):
    """Dapatkan detail mahasiswa"""
    try:
        logger.info(f"Getting details for student ID: {id_reg_pd}")
        # Dapatkan detail mahasiswa
        detail_url = f"https://api-pddikti-admin.kemdikbud.go.id/mahasiswa/detail/{id_reg_pd}?id_pengguna={i_iduser}&id_unit={id_organisasi}&id_role=3&pm={pm_token}"
        
        try:
            response = await asyncio.wait_for(
                session.get(detail_url, headers={
                    "User-Agent": "Mozilla/5.0",
                    "Origin": "https://pddikti-admin.kemdikbud.go.id",
                    "Referer": "https://pddikti-admin.kemdikbud.go.id/",
                    "Content-Type": "application/json"
                }),
                timeout=60.0
            )
            
            if response.status == 200:
                logger.info(f"Successfully retrieved details for student ID: {id_reg_pd}")
                data = await response.json()
                return data.get("result", {})
            else:
                logger.error(f"Get detail failed with status {response.status}")
                try:
                    error_text = await response.text()
                    logger.error(f"Error response: {error_text[:200]}")
                except:
                    pass
                return {}
        except asyncio.TimeoutError:
            logger.error(f"Timeout when getting details for student ID: {id_reg_pd}")
            return {}
                
    except aiohttp.ClientError as e:
        logger.error(f"Network error getting student detail: {str(e)}")
        return {}
    except asyncio.TimeoutError:
        logger.error(f"Timeout getting student detail for ID: {id_reg_pd}")
        return {}
    except Exception as e:
        logger.error(f"Error getting student detail: {str(e)}", exc_info=True)
        return {} 