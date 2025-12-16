import os
from pathlib import Path

import pytest

from cpolar_connect.config import CpolarConfig
from cpolar_connect.ssh import SSHManager
from cpolar_connect.tunnel import TunnelInfo


@pytest.fixture
def ssh_manager(monkeypatch, tmp_path: Path):
    """Create SSHManager with isolated paths"""
    monkeypatch.setenv("CPOLAR_LANG", "en")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    config = CpolarConfig(
        username="test@example.com",
        server_user="ubuntu",
        ssh_key_path=str(tmp_path / ".ssh" / "id_rsa_cpolar"),
        ssh_host_alias="cpolar-server",
    )
    return SSHManager(config)


@pytest.fixture
def tunnel_info():
    """Create test TunnelInfo"""
    return TunnelInfo(
        url="tcp://test.cpolar.io:12345",
        hostname="test.cpolar.io",
        port=12345,
    )


class TestUpdateSshConfig:
    """Tests for SSHManager.update_ssh_config"""

    def test_append_new_host_block(self, ssh_manager, tunnel_info, tmp_path):
        """Test appending a new host block to empty config"""
        ssh_manager.update_ssh_config(tunnel_info)

        config_content = ssh_manager.ssh_config_path.read_text()
        lines = config_content.splitlines()

        # Should have Host block without leading empty lines
        assert lines[0] == "# SSH config file"
        assert lines[1] == ""  # One blank line for separation
        assert lines[2] == "Host cpolar-server"

    def test_update_existing_host_block_no_extra_newlines(
        self, ssh_manager, tunnel_info, tmp_path
    ):
        """Test that updating existing host block does not accumulate empty lines"""
        # First update
        ssh_manager.update_ssh_config(tunnel_info)

        # Count empty lines before Host block
        def count_empty_lines_before_host(content):
            lines = content.splitlines()
            count = 0
            for i, line in enumerate(lines):
                if line == "Host cpolar-server":
                    # Count consecutive empty lines before this
                    j = i - 1
                    while j >= 0 and lines[j].strip() == "":
                        count += 1
                        j -= 1
                    break
            return count

        initial_empty_lines = count_empty_lines_before_host(
            ssh_manager.ssh_config_path.read_text()
        )

        # Update multiple times with different tunnel info
        for port in [22222, 33333, 44444]:
            new_tunnel = TunnelInfo(
                url=f"tcp://new.cpolar.io:{port}",
                hostname="new.cpolar.io",
                port=port,
            )
            ssh_manager.update_ssh_config(new_tunnel)

        final_empty_lines = count_empty_lines_before_host(
            ssh_manager.ssh_config_path.read_text()
        )

        # Empty lines should not accumulate
        assert final_empty_lines == initial_empty_lines

    def test_update_preserves_other_hosts(self, ssh_manager, tunnel_info, tmp_path):
        """Test that updating does not affect other Host blocks"""
        # Create config with another host
        ssh_manager.ssh_config_path.parent.mkdir(parents=True, exist_ok=True)
        ssh_manager.ssh_config_path.write_text(
            "Host other-server\n"
            "\tHostName other.example.com\n"
            "\tPort 22\n"
            "\n"
            "Host cpolar-server\n"
            "\tHostName old.cpolar.io\n"
            "\tPort 11111\n"
        )

        ssh_manager.update_ssh_config(tunnel_info)

        config_content = ssh_manager.ssh_config_path.read_text()

        # Other host should be preserved
        assert "Host other-server" in config_content
        assert "other.example.com" in config_content

        # Cpolar host should be updated
        assert "test.cpolar.io" in config_content
        assert "12345" in config_content

    def test_config_content_correctness(self, ssh_manager, tunnel_info, tmp_path):
        """Test that config content is correct"""
        ssh_manager.update_ssh_config(tunnel_info)

        config_content = ssh_manager.ssh_config_path.read_text()

        assert "Host cpolar-server" in config_content
        assert "HostName test.cpolar.io" in config_content
        assert "Port 12345" in config_content
        assert "User ubuntu" in config_content
        assert "StrictHostKeyChecking no" in config_content

    def test_update_preserves_match_block(self, ssh_manager, tunnel_info, tmp_path):
        """Test that Match blocks after cpolar-server are not deleted"""
        ssh_manager.ssh_config_path.parent.mkdir(parents=True, exist_ok=True)
        ssh_manager.ssh_config_path.write_text(
            "Host cpolar-server\n"
            "\tHostName old.cpolar.io\n"
            "\tPort 11111\n"
            "\n"
            "Match host example.com\n"
            "\tUser special\n"
            "\tForwardAgent yes\n"
        )

        ssh_manager.update_ssh_config(tunnel_info)

        config_content = ssh_manager.ssh_config_path.read_text()

        # Match block should be preserved
        assert "Match host example.com" in config_content
        assert "User special" in config_content
        assert "ForwardAgent yes" in config_content

        # Cpolar host should be updated
        assert "test.cpolar.io" in config_content

    def test_update_preserves_blank_line_between_blocks(
        self, ssh_manager, tunnel_info, tmp_path
    ):
        """Test that blank lines between Host blocks are preserved"""
        ssh_manager.ssh_config_path.parent.mkdir(parents=True, exist_ok=True)
        ssh_manager.ssh_config_path.write_text(
            "Host cpolar-server\n"
            "\tHostName old.cpolar.io\n"
            "\tPort 11111\n"
            "\n"
            "Host other-server\n"
            "\tHostName other.example.com\n"
        )

        ssh_manager.update_ssh_config(tunnel_info)

        config_content = ssh_manager.ssh_config_path.read_text()
        lines = config_content.splitlines()

        # Find the blank line between blocks
        cpolar_end = None
        other_start = None
        for i, line in enumerate(lines):
            if line == "Host cpolar-server":
                # Find where cpolar block content ends
                for j in range(i + 1, len(lines)):
                    if not lines[j].startswith("\t"):
                        cpolar_end = j
                        break
            if line == "Host other-server":
                other_start = i

        # There should be a blank line between the blocks
        assert cpolar_end is not None
        assert other_start is not None
        assert cpolar_end < other_start
        assert lines[cpolar_end] == ""
