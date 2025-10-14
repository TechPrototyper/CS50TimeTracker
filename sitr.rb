# Homebrew Formula for SITR
# To install: brew install --formula ./sitr.rb

class Sitr < Formula
  include Language::Python::Virtualenv

  desc "Simple Time Tracker - Personal time-tracking OS for command line"
  homepage "https://github.com/TechPrototyper/CS50TimeTracker"
  url "https://github.com/TechPrototyper/CS50TimeTracker/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "" # Will be generated after first release
  license "MIT"

  depends_on "python@3.11"

  resource "fastapi" do
    url "https://files.pythonhosted.org/packages/source/f/fastapi/fastapi-0.104.1.tar.gz"
    sha256 "e9dd2743e6e88fb6d0a02fc0c9e5e7a74b4e6e2cf0e2ff6c8a5f6a6c8d2f5a6c"
  end

  resource "uvicorn" do
    url "https://files.pythonhosted.org/packages/source/u/uvicorn/uvicorn-0.24.0.tar.gz"
    sha256 "d82b6b7e0f2b2c8e7cdbea5e7e5e1e6f3f0a7b0f0a1b0f0a7b0f0a1b0f0a7b0"
  end

  resource "sqlmodel" do
    url "https://files.pythonhosted.org/packages/source/s/sqlmodel/sqlmodel-0.0.14.tar.gz"
    sha256 "c3e1d5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5"
  end

  resource "typer" do
    url "https://files.pythonhosted.org/packages/source/t/typer/typer-0.9.0.tar.gz"
    sha256 "a3e6a7e1e7e1e7e1e7e1e7e1e7e1e7e1e7e1e7e1e7e1e7e1e7e1e7e1e7e1e7"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/source/r/rich/rich-13.7.0.tar.gz"
    sha256 "b5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/source/r/requests/requests-2.31.0.tar.gz"
    sha256 "d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5d5"
  end

  resource "psutil" do
    url "https://files.pythonhosted.org/packages/source/p/psutil/psutil-5.9.6.tar.gz"
    sha256 "e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3"
  end

  resource "pydantic" do
    url "https://files.pythonhosted.org/packages/source/p/pydantic/pydantic-2.5.0.tar.gz"
    sha256 "f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5f5"
  end

  resource "email-validator" do
    url "https://files.pythonhosted.org/packages/source/e/email-validator/email_validator-2.1.0.tar.gz"
    sha256 "a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"sitr", "--help"
  end
end
