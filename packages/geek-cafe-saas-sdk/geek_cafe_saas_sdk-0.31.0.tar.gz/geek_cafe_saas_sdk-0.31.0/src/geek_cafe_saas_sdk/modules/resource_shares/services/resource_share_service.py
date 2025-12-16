"""
ResourceShareService for permission-based resource sharing.

Geek Cafe, LLC
MIT License. See Project Root for the license information.
"""

from typing import Dict, Any, Optional, List
from geek_cafe_saas_sdk.core.services.database_service import DatabaseService
from geek_cafe_saas_sdk.core.service_result import ServiceResult
from geek_cafe_saas_sdk.core.service_errors import ValidationError, NotFoundError, AccessDeniedError
from geek_cafe_saas_sdk.core.error_codes import ErrorCode
from geek_cafe_saas_sdk.lambda_handlers import service_method, validate_enum
from ..models.resource_share import ResourceShare
import datetime as dt


class ResourceShareService(DatabaseService[ResourceShare]):
    """
    Generic resource share service for permission-based sharing.
    
    Supports sharing any resource type (files, contacts, projects, etc.)
    with other users with specific permission levels.
    
    Handles:
    - Creating resource shares with permissions
    - Access validation
    - Share expiration
    - Share revocation
    - Permission management (view, download, edit)
    
    Resource Types (examples):
    - "file": File sharing
    - "contact": Contact sharing
    - "project": Project sharing
    - "report": Report sharing
    """
    
    @service_method("create")
    @validate_enum('permission', {'view', 'download', 'edit'})
    def create(
        self,
        resource_id: str,
        resource_type: str,
        shared_with_user_id: str,
        permission: str = "view",
        expires_at_ts: Optional[float] = None,
        can_re_share: bool = False,
        **kwargs
    ) -> ServiceResult[ResourceShare]:
        """
        Create a resource share.
        
        Args:
            resource_id: ID of the resource to share
            resource_type: Type of resource (e.g., "file", "contact", "project")
            shared_with_user_id: User ID to share with
            permission: Permission level (view, download, edit)
            expires_at_ts: Optional expiration timestamp
            can_re_share: Whether recipient can re-share
            
        Returns:
            ServiceResult with ResourceShare model
        """
        self.request_context.require_authentication()
        
        tenant_id = self.request_context.target_tenant_id
        user_id = self.request_context.target_user_id
        
        # Validation
        if not resource_id:
            raise ValidationError("resource_id is required", "resource_id")
        
        if not resource_type:
            raise ValidationError("resource_type is required", "resource_type")
        
        if not shared_with_user_id:
            raise ValidationError("shared_with_user_id is required", "shared_with_user_id")
        
        if shared_with_user_id == user_id:
            raise ValidationError(
                "Cannot share resource with yourself",
                "shared_with_user_id"
            )
        
        # Check for existing active share
        existing_share = self._get_existing_share(
            resource_id, shared_with_user_id
        )
        if existing_share:
            raise ValidationError(
                "Resource is already shared with this user",
                "shared_with_user_id"
            )
        
        # Create ResourceShare model
        share = ResourceShare()
        share.tenant_id = tenant_id
        share.resource_id = resource_id
        share.resource_type = resource_type        
        share.owner_id = user_id
        share.shared_with_user_id = shared_with_user_id
        share.permission_level = permission
        share.expires_at_ts = expires_at_ts
        share.can_re_share = can_re_share
        share.status = "active"
        share.access_count = 0
        
        # Save to DynamoDB
        share.prep_for_save()
        return self._save_model(share)
    
    @service_method("get_by_id")
    def get_by_id(self, share_id: str) -> ServiceResult[ResourceShare]:
        """
        Get share by ID.
        
        Args:
            share_id: Share ID
            
        Returns:
            ServiceResult with ResourceShare model
        """
        self.request_context.require_authentication()
        
        tenant_id = self.request_context.target_tenant_id
        user_id = self.request_context.target_user_id
        
        share = self._get_model_by_id_with_tenant_check(share_id, ResourceShare, tenant_id)
        
        if not share:
            raise NotFoundError(f"Share not found: {share_id}")
        
        # Access control: user must be sharer or sharee
        if share.owner_id != user_id and share.shared_with_user_id != user_id:
            raise AccessDeniedError("You do not have access to this share")
        
        return ServiceResult.success_result(share)
    
    @service_method("update")
    def update(self, share_id: str, **kwargs) -> ServiceResult[ResourceShare]:
        """
        Update share (permission or expiration).
        
        Args:
            share_id: Share ID
            **kwargs: Fields to update (permission_level, expires_at_ts, can_re_share)
            
        Returns:
            ServiceResult with updated ResourceShare model
        """
        self.request_context.require_authentication()
        
        user_id = self.request_context.target_user_id
        
        # Get existing share
        get_result = self.get_by_id(share_id)
        if not get_result.success:
            return get_result
        
        share = get_result.data
        
        # Only sharer can update
        if share.owner_id != user_id:
            raise AccessDeniedError("Only the person who shared can update this share")
        
        # Apply updates (only allowed fields)
        allowed_fields = ["permission_level", "expires_at_ts", "can_re_share"]
        
        for field, value in kwargs.items():
            if field == "permission_level":
                valid_permissions = ["view", "download", "edit"]
                if value not in valid_permissions:
                    raise ValidationError(
                        f"Invalid permission: {value}",
                        "permission_level"
                    )
            
            if field in allowed_fields:
                setattr(share, field, value)
        
        share.modified_utc_ts = dt.datetime.now(dt.UTC).timestamp()
        
        # Save to DynamoDB
        share.prep_for_save()
        return self._save_model(share)
    
    @service_method("delete")
    def delete(self, share_id: str) -> ServiceResult[bool]:
        """
        Delete (revoke) a share. Alias for revoke().
        
        Args:
            share_id: Share ID
            
        Returns:
            ServiceResult with success boolean
        """
        return self.revoke(share_id)
    
    @service_method("revoke")
    def revoke(self, share_id: str) -> ServiceResult[bool]:
        """
        Revoke a share.
        
        Args:
            share_id: Share ID
            
        Returns:
            ServiceResult with success boolean
        """
        self.request_context.require_authentication()
        
        user_id = self.request_context.target_user_id
        
        # Get existing share
        get_result = self.get_by_id(share_id)
        if not get_result.success:
            return get_result
        
        share = get_result.data
        
        # Only sharer can revoke
        if share.owner_id != user_id:
            raise AccessDeniedError("Only the person who shared can revoke this share")
        
        # Use model's revoke method
        share.revoke()
        
        share.prep_for_save()
        save_result = self._save_model(share)
        
        if not save_result.success:
            return save_result
        
        return ServiceResult.success_result(True)
    
    @service_method("list_by_resource")
    def list_by_resource(
        self,
        resource_id: str,
        resource_type: str,
        include_revoked: bool = False,
        limit: int = 50
    ) -> ServiceResult[List[ResourceShare]]:
        """
        List all shares for a resource.
        
        Args:
            resource_id: Resource ID
            resource_type: Resource type
            include_revoked: Whether to include revoked shares
            limit: Maximum number of results
            
        Returns:
            ServiceResult with list of ResourceShare models
        """
        self.request_context.require_authentication()
        
        # Use GSI1 to query shares by resource
        temp_share = ResourceShare()
        temp_share.resource_id = resource_id
        
        query_result = self._query_by_index(temp_share, "gsi1", limit=limit, ascending=False)
        
        if not query_result.success:
            return query_result
        
        # Filter results
        shares = []
        for share in query_result.data:
            # Filter by resource_type
            if share.resource_type != resource_type:
                continue
            # Filter out revoked unless requested
            if not include_revoked and share.status == "revoked":
                continue
            shares.append(share)
        
        return ServiceResult.success_result(shares)
    
    @service_method("list_shared_with_me")
    def list_shared_with_me(
        self,
        resource_type: Optional[str] = None,
        limit: int = 50
    ) -> ServiceResult[List[ResourceShare]]:
        """
        List all resources shared with current user.
        
        Args:
            resource_type: Optional filter by resource type
            limit: Maximum number of results
            
        Returns:
            ServiceResult with list of ResourceShare models
        """
        self.request_context.require_authentication()
        
        user_id = self.request_context.target_user_id
        
        # Use GSI2 to query shares by shared_with_user
        temp_share = ResourceShare()
        temp_share.shared_with_user_id = user_id
        
        query_result = self._query_by_index(temp_share, "gsi2", limit=limit, ascending=False)
        
        if not query_result.success:
            return query_result
        
        # Filter results
        shares = []
        for share in query_result.data:
            # Filter by resource_type if specified
            if resource_type and share.resource_type != resource_type:
                continue
            # Only include active, non-expired shares
            if share.is_active() and not share.is_expired():
                shares.append(share)
        
        return ServiceResult.success_result(shares)
    
    @service_method("check_access")
    def check_access(
        self,
        resource_id: str,        
        required_permission: str = "view"
    ) -> ServiceResult[Dict[str, Any]]:
        """
        Check if current user has access to a resource via sharing.
        
        Args:
            resource_id: Resource ID
            required_permission: Required permission level
            
        Returns:
            ServiceResult with access info (has_access, permission, reason)
        """
        user_id = self.request_context.target_user_id
        
        # Check for active share
        share = self._get_existing_share(resource_id, user_id)
        
        if not share:
            return ServiceResult.success_result({
                "has_access": False,
                "permission": None,
                "reason": "no_share"
            })
        
        # Check if share is active
        if not share.is_active():
            return ServiceResult.success_result({
                "has_access": False,
                "permission": None,
                "reason": "revoked"
            })
        
        # Check if share is expired
        if share.is_expired():
            return ServiceResult.success_result({
                "has_access": False,
                "permission": None,
                "reason": "expired"
            })
        
        # Check permission level using model's method
        has_access = share.has_permission(required_permission)
        
        # Increment access count if accessing
        if has_access:
            self._increment_access_count(share)
        
        return ServiceResult.success_result({
            "has_access": has_access,
            "permission": share.permission_level,
            "reason": "granted" if has_access else "insufficient_permission"
        })
    
    # Helper methods
    
    def _get_existing_share(
        self,
        resource_id: str,        
        shared_with_user_id: str
    ) -> Optional[ResourceShare]:
        """Check if an active share already exists for this resource and user."""
        try:
            tenant_id = self.request_context.target_tenant_id
            
            # Query GSI1 by resource_id to get all shares for this resource
            temp_share = ResourceShare()
            temp_share.resource_id = resource_id
            
            result = self._query_by_index(temp_share, "gsi1", limit=100)
            
            if not result.success:
                return None
            
            # Filter for matching tenant, resource_type, user, and active status
            for share in result.data:
                if (share.tenant_id == tenant_id and
                    share.shared_with_user_id == shared_with_user_id and
                    share.status == "active"):
                    return share
            
            return None
            
        except Exception:
            return None
    
    def _increment_access_count(self, share: ResourceShare) -> None:
        """Increment share access count (best effort)."""
        try:
            share.increment_access_count()
            share.prep_for_save()
            self._save_model(share)
        except Exception:
            pass  # Best effort - don't fail the access check
