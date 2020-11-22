;;; arwa.el --- ARWA -*- lexical-binding: t; -*-

;; Copyright (c) 2020 Abhinav Tushar

;; Author: Abhinav Tushar <abhinav@lepisma.xyz>
;; Version: 0.0.1
;; Package-Requires: ((emacs "27"))
;; URL: https://github.com/lepisma/arwa

;;; Commentary:

;; ARWA
;; This file is not a part of GNU Emacs.

;;; License:

;; This program is free software: you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with this program. If not, see <https://www.gnu.org/licenses/>.

;;; Code:

(defcustom arwa-root-dir (expand-file-name "~/.tofish/p/arwa")
  "Path to arwa project. This is a temporary development mode thing.")

(defvar arwa-slack-temp-file "/tmp/arwa-slack.md")

(defun arwa-exec (command)
  (let ((default-directory arwa-root-dir))
    (shell-command-to-string (format "fish -c \"direnv allow; direnv exec ./ %s\"" command))))

(defun arwa-post (channel-name)
  (arwa-exec (format "poetry run arwa slack post --text-file=%s --channel-name=%s" arwa-slack-temp-file channel-name)))

(defun arwa-post-to-channel (channel-name)
  "Post content of current buffer to CHANNEL-NAME."
  (interactive "sChannel name: ")
  (let ((text (buffer-string)))
    (with-current-buffer (find-file-noselect arwa-slack-temp-file)
      (erase-buffer)
      (insert text)
      (save-buffer)
      (kill-buffer))
    (arwa-post channel-name)))

(provide 'arwa)

;;; arwa.el ends here
