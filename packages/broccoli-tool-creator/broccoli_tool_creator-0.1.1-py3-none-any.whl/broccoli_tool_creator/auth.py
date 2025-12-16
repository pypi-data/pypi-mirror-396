import requests
import json
import hmac
import hashlib
import base64
import secrets
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional

class CognitoSRPAuth:
    """
    AWS Cognito SRP Authentication Implementation
    
    The PASSWORD_CLAIM_SIGNATURE is calculated through the SRP protocol:
    1. Client generates random 'a' and calculates A = g^a mod N
    2. Server responds with B, salt, and SECRET_BLOCK
    3. Client calculates shared secret 'S' using password and SRP values
    4. Client derives HKDF key from S
    5. Client signs the claim using HMAC-SHA256
    """
    
    def __init__(self, client_id: str, username: str, password: str, pool_id: str):
        self.client_id = client_id
        self.username = username
        self.password = password
        self.pool_id = pool_id
        # Extract region from pool_id (e.g. ap-south-1_xxxx -> ap-south-1)
        self.region = pool_id.split('_')[0]
        self.base_url = f"https://cognito-idp.{self.region}.amazonaws.com/"
        
        # AWS Cognito uses a specific large prime N for SRP
        # This is the complete 3072-bit prime from the warrant library
        self.N_hex = (
            "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
            "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
            "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
            "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
            "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
            "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
            "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
            "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
            "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
            "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
            "15728E5A8AAAC42DAD33170D04507A33A85521ABDF1CBA64"
            "ECFB850458DBEF0A8AEA71575D060C7DB3970F85A6E1E4C7"
            "ABF5AE8CDB0933D71E8C94E04A25619DCEE3D2261AD2EE6B"
            "F12FFA06D98A0864D87602733EC86A64521F2B18177B200C"
            "BBE117577A615D6C770988C0BAD946E208E24FA074E5AB31"
            "43DB5BFCE0FD108E4B82D120A93AD2CAFFFFFFFFFFFFFFFF"
        )
        self.N = int(self.N_hex, 16)
        self.g = 2
        
        # For storing SRP values during authentication
        self.a = None
        self.A = None
        
    def get_headers(self, target: str) -> Dict[str, str]:
        """Generate request headers for Cognito API calls"""
        return {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-store',
            'content-type': 'application/x-amz-json-1.1',
            # Origin and Referer might need to be dynamic or configured, 
            # but for now we keep the working values
            'origin': 'https://dev2-broccoli.dailoqa.com',
            'referer': 'https://dev2-broccoli.dailoqa.com/login',
            'x-amz-target': target,
            'x-amz-user-agent': 'aws-amplify/5.0.4'
        }
    
    def hash_sha256(self, data: bytes) -> bytes:
        """SHA256 hash helper"""
        return hashlib.sha256(data).digest()
    
    def pad_hex(self, long_int: Any) -> str:
        """
        Converts a Long integer (or hex string) to hex format padded with zeroes for hashing
        This matches the warrant library implementation
        """
        if not isinstance(long_int, str):
            hash_str = self.long_to_hex(long_int)
        else:
            hash_str = long_int
        # Pad with leading zero if odd length
        if len(hash_str) % 2 == 1:
            hash_str = '0' + hash_str
        # Add '00' prefix if first char is in upper half of hex range
        # This is critical for proper SRP implementation
        elif hash_str[0] in '89ABCDEFabcdef':
            hash_str = '00' + hash_str
        return hash_str
    
    def hex_hash(self, hex_string: str) -> str:
        """Hash a hex string"""
        # Ensure the hex string is properly padded
        hex_string = self.pad_hex(hex_string)
        return hashlib.sha256(bytes.fromhex(hex_string)).hexdigest()
    
    def hex_to_long(self, hex_string: str) -> int:
        """Convert hex string to long integer"""
        return int(hex_string, 16)
    
    def long_to_hex(self, long_num: int) -> str:
        """Convert long integer to hex string"""
        hex_str = format(long_num, 'x')
        return self.pad_hex(hex_str)
    
    def get_random(self, nbytes: int) -> bytes:
        """Generate random bytes"""
        return secrets.token_bytes(nbytes)
    
    def calculate_u(self, big_a: int, big_b: int) -> int:
        """
        Calculate the client's value U which is the hash of A and B
        :param big_a: Large A value (integer)
        :param big_b: Server B value (integer)
        :return: Computed U value
        """
        u_hex_hash = self.hex_hash(self.pad_hex(big_a) + self.pad_hex(big_b))
        return self.hex_to_long(u_hex_hash)
    
    def generate_srp_a_and_A(self) -> str:
        """
        Generate SRP values:
        - a: random private value
        - A: g^a mod N (public value sent to server)
        """
        # Generate random 'a' (128 bytes = 1024 bits)
        random_bytes = self.get_random(128)
        self.a = self.hex_to_long(random_bytes.hex())
        
        # Calculate A = g^a mod N
        self.A = pow(self.g, self.a, self.N)
        
        # Return A as hex string (padded)
        return self.long_to_hex(self.A)
    
    def calculate_shared_secret(self, username: str, password: str, pool_name: str, salt_hex: str, srp_b_hex: str) -> int:
        """
        Calculate the SRP shared secret 'S'
        This is the core of SRP - deriving shared secret without sending password
        
        Steps:
        1. Calculate u = H(A, B)
        2. Calculate x = H(salt, H(poolName, username, password))
        3. Calculate S = (B - k*g^x)^(a + u*x) mod N
        """
        # Ensure B is properly padded
        srp_b_hex = self.pad_hex(srp_b_hex)
        B = self.hex_to_long(srp_b_hex)
        
        # Calculate u = H(A, B)
        u = self.calculate_u(self.A, B)
        if u == 0:
            raise ValueError('U cannot be zero.')
        
        # Calculate k = H(N, g)
        # Note the '00' and '0' prefixes - critical for AWS Cognito
        k_hex = self.hex_hash('00' + self.N_hex + '0' + format(self.g, 'x'))
        k = self.hex_to_long(k_hex)
        
        # Calculate x = H(salt | H(userPoolName | username | ":" | password))
        # First, hash the user credentials
        # Use only the pool ID part (after underscore) from full pool
        user_pass = f"{pool_name}{username}:{password}"
        user_pass_hash = self.hash_sha256(user_pass.encode('utf-8')).hex()
        user_pass_hash = (64 - len(user_pass_hash)) * '0' + user_pass_hash
        
        # Then hash with salt
        x_hex = self.hex_hash(self.pad_hex(salt_hex) + user_pass_hash)
        x = self.hex_to_long(x_hex)
        
        # Calculate g^x mod N
        g_mod_pow_xn = pow(self.g, x, self.N)
        
        # Calculate intermediate value: B - k*g^x
        int_value = (B - k * g_mod_pow_xn) % self.N
        
        # Calculate S = (B - k*g^x)^(a + u*x) mod N
        S = pow(int_value, (self.a + u * x), self.N)
        
        return S
    
    def compute_hkdf(self, ikm: bytes, salt: bytes) -> bytes:
        """
        Compute HKDF (HMAC-based Key Derivation Function)
        Used to derive the signing key from shared secret
        
        HKDF-Extract:
        PRK = HMAC-SHA256(salt, IKM)
        
        HKDF-Expand:
        OKM = HMAC-SHA256(PRK, info | 0x01)
        """
        # HKDF-Extract
        prk = hmac.new(salt, ikm, hashlib.sha256).digest()
        
        # HKDF-Expand with info = "Caldera Derived Key" and length = 16
        info = b"Caldera Derived Key"
        okm = hmac.new(prk, info + bytes([1]), hashlib.sha256).digest()
        
        return okm[:16]  # Return first 16 bytes
    
    def calculate_signature(self, username: str, password: str, pool_name: str, salt_hex: str, srp_b_hex: str, 
                          secret_block: str, timestamp: str) -> str:
        """
        Calculate the PASSWORD_CLAIM_SIGNATURE
        
        This is the final step that proves we know the password:
        1. Calculate shared secret S using SRP
        2. Derive HKDF key from S and u
        3. Create message from username, secret_block, timestamp
        4. Sign message with HMAC-SHA256 using derived key
        5. Base64 encode the signature
        """
        # print("\n[SECRET] Calculating PASSWORD_CLAIM_SIGNATURE...")
        
        # Step 1: Calculate shared secret S
        S = self.calculate_shared_secret(username, password, pool_name, 
                                        salt_hex, srp_b_hex)
        # print(f"  + Calculated shared secret S")
        
        # Step 2: Calculate u for HKDF salt
        u = self.calculate_u(self.A, self.hex_to_long(srp_b_hex))
        
        # Step 3: Derive key using HKDF
        # Convert S and u to bytes using pad_hex
        s_bytes = bytes.fromhex(self.pad_hex(S))
        u_bytes = bytes.fromhex(self.pad_hex(self.long_to_hex(u)))
        hkdf_key = self.compute_hkdf(s_bytes, u_bytes)
        # print(f"  + Derived HKDF signing key")
        
        # Step 4: Create message to sign
        # Format: poolName + userId + secretBlock + timestamp
        msg = pool_name.encode('utf-8')
        msg += username.encode('utf-8')
        msg += base64.standard_b64decode(secret_block)
        msg += timestamp.encode('utf-8')
        # print(f"  + Created message to sign")
        
        # Step 5: Sign with HMAC-SHA256
        signature = hmac.new(hkdf_key, msg, hashlib.sha256).digest()
        signature_b64 = base64.standard_b64encode(signature).decode('utf-8')
        # print(f"  + Generated signature: {signature_b64[:30]}...")
        
        return signature_b64
    
    def initiate_auth(self) -> Optional[Dict[str, Any]]:
        """
        Step 1: Initiate SRP authentication
        Sends SRP_A to server and receives challenge parameters
        """
        # print("\n" + "="*60)
        # print("Step 1: InitiateAuth - Starting SRP flow")
        # print("="*60)
        
        # Generate SRP A value
        srp_a_hex = self.generate_srp_a_and_A()
        # print(f"Generated SRP_A: {srp_a_hex[:50]}...")
        
        payload = {
            "AuthFlow": "USER_SRP_AUTH",
            "ClientId": self.client_id,
            "AuthParameters": {
                "USERNAME": self.username,
                "SRP_A": srp_a_hex
            },
            "ClientMetadata": {}
        }
        
        response = requests.post(
            self.base_url,
            headers=self.get_headers("AWSCognitoIdentityProviderService.InitiateAuth"),
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            # print("+ InitiateAuth successful - received challenge")
            return result
        else:
            print(f"- InitiateAuth failed: {response.status_code}")
            print(response.text)
            return None
    
    def respond_to_challenge(self, challenge_params: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Step 2: Respond to PASSWORD_VERIFIER challenge
        Calculate signature and send response to complete authentication
        """
        # print("\n" + "="*60)
        # print("Step 2: RespondToAuthChallenge - Proving password knowledge")
        # print("="*60)
        
        # Extract challenge parameters
        salt = challenge_params.get("SALT")
        srp_b = challenge_params.get("SRP_B")
        secret_block = challenge_params.get("SECRET_BLOCK")
        user_id = challenge_params.get("USER_ID_FOR_SRP")
        
        # print(f"Received SALT: {salt[:20]}...")
        # print(f"Received SRP_B: {srp_b[:50]}...")
        # print(f"Received SECRET_BLOCK: {secret_block[:50]}...")
        # print(f"User ID: {user_id}")
        
        # Generate timestamp - AWS Cognito requires day without leading zero
        timestamp = datetime.now(timezone.utc).strftime("%a %b %d %H:%M:%S UTC %Y")
        # Strip leading zero from day number (required by AWS Cognito)
        timestamp = re.sub(r" 0(\d) ", r" \1 ", timestamp)
        # print(f"Timestamp: {timestamp}")
        
        # Extract pool name from user pool (format: region_poolId)
        # For Cognito, use only the pool ID part (after underscore)
        pool_name = self.pool_id.split('_')[1]
        
        # Calculate the signature
        signature = self.calculate_signature(
            user_id,
            self.password,
            pool_name,
            salt,
            srp_b,
            secret_block,
            timestamp
        )
        
        # Prepare challenge response
        challenge_responses = {
            "USERNAME": user_id,
            "PASSWORD_CLAIM_SECRET_BLOCK": secret_block,
            "TIMESTAMP": timestamp,
            "PASSWORD_CLAIM_SIGNATURE": signature
        }
        
        payload = {
            "ChallengeName": "PASSWORD_VERIFIER",
            "ClientId": self.client_id,
            "ChallengeResponses": challenge_responses,
            "ClientMetadata": {}
        }
        
        # print("\nSending challenge response...")
        response = requests.post(
            self.base_url,
            headers=self.get_headers("AWSCognitoIdentityProviderService.RespondToAuthChallenge"),
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            # print("+ Challenge response successful!")
            return result
        else:
            print(f"- Challenge response failed: {response.status_code}")
            print(response.text)
            return None
    
    def authenticate(self) -> Optional[Dict[str, Any]]:
        """
        Main authentication flow
        Returns access token and other authentication tokens
        """
        # print("\n" + "="*60)
        # print("AWS COGNITO SRP AUTHENTICATION")
        # print("="*60)
        # print(f"User: {self.username}")
        # print(f"Client ID: {self.client_id}")
        
        # Step 1: Initiate Auth
        init_result = self.initiate_auth()
        if not init_result:
            return None
        
        # Extract challenge parameters
        challenge_params = init_result.get("ChallengeParameters", {})
        
        # Step 2: Respond to Challenge
        auth_result = self.respond_to_challenge(challenge_params)
        if not auth_result:
            return None
        
        # Extract tokens
        auth_data = auth_result.get("AuthenticationResult", {})
        access_token = auth_data.get("AccessToken")
        id_token = auth_data.get("IdToken")
        refresh_token = auth_data.get("RefreshToken")
        expires_in = auth_data.get("ExpiresIn")
        
        # print("\n" + "="*60)
        # print("[SUCCESS] AUTHENTICATION SUCCESSFUL!")
        # print("="*60)
        
        return {
            "access_token": access_token,
            "id_token": id_token,
            "refresh_token": refresh_token,
            "expires_in": expires_in
        }
