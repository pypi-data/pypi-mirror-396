import React from 'react'
import './Input.css'

/**
 * Input Component - Text input field
 */
export const Input = React.forwardRef(
  (
    {
      label,
      error,
      helperText,
      className = '',
      fullWidth = false,
      ...props
    },
    ref
  ) => {
    const inputId = props.id || `input-${Math.random().toString(36).substr(2, 9)}`
    const classes = [
      'ui-input-wrapper',
      error && 'ui-input-wrapper--error',
      fullWidth && 'ui-input-wrapper--full-width',
      className,
    ]
      .filter(Boolean)
      .join(' ')

    return (
      <div className={classes}>
        {label && (
          <label htmlFor={inputId} className="ui-input-label">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className="ui-input"
          {...props}
        />
        {error && <span className="ui-input-error">{error}</span>}
        {helperText && !error && (
          <span className="ui-input-helper">{helperText}</span>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

/**
 * Select Component
 */
export const Select = React.forwardRef(
  (
    {
      label,
      error,
      helperText,
      className = '',
      fullWidth = false,
      children,
      ...props
    },
    ref
  ) => {
    const selectId = props.id || `select-${Math.random().toString(36).substr(2, 9)}`
    const classes = [
      'ui-input-wrapper',
      error && 'ui-input-wrapper--error',
      fullWidth && 'ui-input-wrapper--full-width',
      className,
    ]
      .filter(Boolean)
      .join(' ')

    return (
      <div className={classes}>
        {label && (
          <label htmlFor={selectId} className="ui-input-label">
            {label}
          </label>
        )}
        <select ref={ref} id={selectId} className="ui-select" {...props}>
          {children}
        </select>
        {error && <span className="ui-input-error">{error}</span>}
        {helperText && !error && (
          <span className="ui-input-helper">{helperText}</span>
        )}
      </div>
    )
  }
)

Select.displayName = 'Select'

/**
 * Textarea Component
 */
export const Textarea = React.forwardRef(
  (
    {
      label,
      error,
      helperText,
      className = '',
      fullWidth = false,
      ...props
    },
    ref
  ) => {
    const textareaId = props.id || `textarea-${Math.random().toString(36).substr(2, 9)}`
    const classes = [
      'ui-input-wrapper',
      error && 'ui-input-wrapper--error',
      fullWidth && 'ui-input-wrapper--full-width',
      className,
    ]
      .filter(Boolean)
      .join(' ')

    return (
      <div className={classes}>
        {label && (
          <label htmlFor={textareaId} className="ui-input-label">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={textareaId}
          className="ui-textarea"
          {...props}
        />
        {error && <span className="ui-input-error">{error}</span>}
        {helperText && !error && (
          <span className="ui-input-helper">{helperText}</span>
        )}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'

export default Input

