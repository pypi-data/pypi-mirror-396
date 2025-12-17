import React, { useEffect } from 'react'
import { X } from 'lucide-react'
import './Modal.css'

/**
 * Modal Component - Reusable modal dialog
 * @param {boolean} open - Modal visibility
 * @param {function} onClose - Close handler
 * @param {string} title - Modal title
 * @param {string} size - 'sm' | 'md' | 'lg' | 'xl' | 'full'
 * @param {boolean} closeOnBackdrop - Close on backdrop click
 * @param {React.ReactNode} children - Modal content
 * @param {React.ReactNode} footer - Modal footer
 */
export const Modal = ({
  open,
  onClose,
  title,
  size = 'md',
  closeOnBackdrop = true,
  children,
  footer,
  className = '',
}) => {
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [open])

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && open && onClose) {
        onClose()
      }
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [open, onClose])

  if (!open) return null

  const handleBackdropClick = (e) => {
    if (closeOnBackdrop && e.target === e.currentTarget && onClose) {
      onClose()
    }
  }

  return (
    <div className="ui-modal-backdrop" onClick={handleBackdropClick}>
      <div className={`ui-modal ui-modal--${size} ${className}`} onClick={(e) => e.stopPropagation()}>
        {title && (
          <div className="ui-modal-header">
            <h3 className="ui-modal-title">{title}</h3>
            {onClose && (
              <button
                className="ui-modal-close"
                onClick={onClose}
                aria-label="بستن"
              >
                <X size={20} />
              </button>
            )}
          </div>
        )}
        <div className="ui-modal-body">{children}</div>
        {footer && <div className="ui-modal-footer">{footer}</div>}
      </div>
    </div>
  )
}

export default Modal

