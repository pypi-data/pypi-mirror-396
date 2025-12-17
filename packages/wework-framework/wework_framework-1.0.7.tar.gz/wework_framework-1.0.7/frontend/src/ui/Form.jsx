import React from 'react'
import './Form.css'

/**
 * FormGroup - Wrapper for form fields
 */
export const FormGroup = ({ className = '', children, ...props }) => {
  return (
    <div className={`ui-form-group ${className}`} {...props}>
      {children}
    </div>
  )
}

/**
 * FormRow - Horizontal form field layout
 */
export const FormRow = ({ className = '', children, columns = 2, ...props }) => {
  return (
    <div
      className={`ui-form-row ui-form-row--${columns} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

/**
 * FormActions - Form action buttons container
 */
export const FormActions = ({ className = '', children, ...props }) => {
  return (
    <div className={`ui-form-actions ${className}`} {...props}>
      {children}
    </div>
  )
}

export default FormGroup

