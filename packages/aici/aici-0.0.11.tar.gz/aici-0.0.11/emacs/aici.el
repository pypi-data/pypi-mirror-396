;;; aici.el --- A brief description of the package

;; Copyright (C) 2024 Taka Suzuki

;; Permission is hereby granted, free of charge, to any person obtaining a copy
;; of this software and associated documentation files (the "Software"), to deal
;; in the Software without restriction, including without limitation the rights
;; to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
;; copies of the Software, and to permit persons to whom the Software is
;; furnished to do so, subject to the following conditions:

;; The above copyright notice and this permission notice shall be included in
;; all copies or substantial portions of the Software.

;; THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
;; IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
;; FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
;; AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
;; LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
;; OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
;; THE SOFTWARE.

;;; Commentary:

;; AICI i/f code

;; for example, assign to your preferred shortcut like.
;; (global-set-key (kbd "C-c j") 'aici-call)


;;; Code:

(defun aici-call ()
  "Send selected region or prompt for input if no region is selected to the 'aici' command and insert the output in real-time."
  (interactive)
  (let* ((text (if (use-region-p)
                   (buffer-substring-no-properties (region-beginning) (region-end))
                 (read-string "Enter text: ")))
         ;; Attempt to create or get the output buffer
         (output-buffer (get-buffer-create "*AICI Output*")))

    ;; Check if the buffer creation was successful
    (if (not output-buffer)
        (error "Failed to create or access the output buffer")
      ;; Clear the output buffer
      (with-current-buffer output-buffer
        (erase-buffer)
        ;; Set the buffer to markdown-mode
        (markdown-mode))

      ;; Display a message indicating that processing is ongoing
      (message "Processing...")

      ;; Start the process and stream the output to the buffer
      (let ((process (start-process "aici-process" output-buffer "sh" "-c"
                                    (format "echo %s | aici -" (shell-quote-argument text)))))
        ;; Set a process filter to handle output streaming
        (set-process-filter process
                            (lambda (proc output)
                              ;; Explicitly reference the output-buffer by capturing it in the lambda
                              (let ((buffer (process-buffer proc)))
                                (when (buffer-live-p buffer)
                                  (with-current-buffer buffer
                                    (goto-char (point-max))
                                    (insert output)
                                    ;; Optionally display the buffer in real-time
                                    (display-buffer buffer))))))

        ;; Set a sentinel to handle process completion
        (set-process-sentinel process
                              (lambda (proc event)
                                ;; Again, ensure that output-buffer is properly referenced
                                (let ((buffer (process-buffer proc)))
                                  (when (buffer-live-p buffer)
                                    (if (string= event "finished\n")
                                        (message "Processing complete.")
                                      (message "Processing interrupted: %s" event))))))))

      ;; Ensure the output buffer is displayed after starting the process
      (display-buffer output-buffer)))

(provide 'aici)



;;; aici.el ends here


