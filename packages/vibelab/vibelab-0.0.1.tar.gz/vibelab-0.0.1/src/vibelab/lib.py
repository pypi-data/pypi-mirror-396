"""Library functions for VibeLab."""

import subprocess
import tempfile
from pathlib import Path

from .models.scenario import GitHubCodeRef


def resolve_github_ref(owner: str, repo: str, ref: str) -> str:
    """
    Resolve a GitHub reference (branch/tag) to a commit SHA.
    
    Args:
        owner: Repository owner
        repo: Repository name
        ref: Branch name, tag, or commit SHA
        
    Returns:
        Commit SHA (full 40-character hash)
        
    Raises:
        ValueError: If the reference cannot be resolved
    """
    # If it's already a full SHA (40 chars), return it
    if len(ref) == 40 and all(c in '0123456789abcdef' for c in ref.lower()):
        return ref
    
    # If it's a short SHA (7+ chars), try to resolve it
    if len(ref) >= 7 and all(c in '0123456789abcdef' for c in ref.lower()):
        # Could be a short SHA, but we'll still resolve via git to be sure
        pass
    
    # Clone to temp directory and resolve the reference
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / repo
        try:
            # Clone with the specific branch/tag (shallow for speed)
            subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", ref, f"https://github.com/{owner}/{repo}.git", str(repo_path)],
                check=True,
                capture_output=True,
            )
            
            # Get the commit SHA
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                check=True,
                capture_output=True,
                text=True,
            )
            
            commit_sha = result.stdout.strip()
            if len(commit_sha) == 40:
                return commit_sha
            
            raise ValueError(f"Could not resolve {ref} to a commit SHA")
            
        except subprocess.CalledProcessError:
            # Fallback: try cloning without branch specification and then checking out
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", f"https://github.com/{owner}/{repo}.git", str(repo_path)],
                    check=True,
                    capture_output=True,
                )
                
                # Try to checkout the reference
                subprocess.run(
                    ["git", "checkout", ref],
                    cwd=repo_path,
                    check=True,
                    capture_output=True,
                )
                
                # Get the commit SHA
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=repo_path,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                
                commit_sha = result.stdout.strip()
                if len(commit_sha) == 40:
                    return commit_sha
            except subprocess.CalledProcessError as e:
                raise ValueError(f"Failed to resolve GitHub reference {ref}: {e.stderr.decode() if e.stderr else str(e)}")
            
            raise ValueError(f"Could not resolve {ref} to a commit SHA")


def resolve_github_code_ref(code_ref: GitHubCodeRef) -> GitHubCodeRef:
    """
    Resolve a GitHub code reference, converting branch/tag names to commit SHAs.
    
    Args:
        code_ref: GitHub code reference (may have branch name instead of commit SHA)
        
    Returns:
        GitHub code reference with resolved commit SHA
    """
    # If commit_sha looks like a branch name (not a SHA), resolve it
    if code_ref.commit_sha and not (
        len(code_ref.commit_sha) >= 7 and 
        all(c in '0123456789abcdef' for c in code_ref.commit_sha.lower())
    ):
        # Looks like a branch/tag name, resolve it
        resolved_sha = resolve_github_ref(code_ref.owner, code_ref.repo, code_ref.commit_sha)
        return GitHubCodeRef(
            owner=code_ref.owner,
            repo=code_ref.repo,
            commit_sha=resolved_sha,
            branch=code_ref.commit_sha,  # Store original branch name
        )
    
    return code_ref
