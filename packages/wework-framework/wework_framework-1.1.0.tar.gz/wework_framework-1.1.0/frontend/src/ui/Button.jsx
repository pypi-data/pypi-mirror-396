import React from 'react'
import './Button.css'

/**
 * Button Component - Reusable button with variants
 * @param {string} variant - 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'ghost'
 * @param {string} size - 'sm' | 'md' | 'lg'
 * @param {boolean} disabled - Disabled state
 * @param {boolean} loading - Loading state
 * @param {string} className - Additional classes
 * @param {React.ReactNode} children - Button content
 * @param {object} ...props - Other button props
 */
export const Button = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  className = '',
  children,
  ...props
}) => {
  const classes = [
    'ui-button',
    `ui-button--${variant}`,
    `ui-button--${size}`,
    loading && 'ui-button--loading',
    className,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <button className={classes} disabled={disabled || loading} {...props}>
      {loading && <span className="ui-button-spinner" />}
      <span className="ui-button-content">{children}</span>
    </button>
  )
}

export default Button

