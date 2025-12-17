import React from 'react'
import './Card.css'

/**
 * Card Component - Reusable card container
 * @param {string} variant - 'default' | 'outlined' | 'elevated'
 * @param {boolean} hover - Enable hover effect
 * @param {string} className - Additional classes
 * @param {React.ReactNode} children - Card content
 * @param {object} ...props - Other div props
 */
export const Card = React.forwardRef(({
  variant = 'default',
  hover = false,
  className = '',
  children,
  ...props
}, ref) => {
  const classes = [
    'ui-card',
    `ui-card--${variant}`,
    hover && 'ui-card--hover',
    className,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <div ref={ref} className={classes} {...props}>
      {children}
    </div>
  )
})

Card.displayName = 'Card'

/**
 * Card Header Component
 */
export const CardHeader = ({ className = '', children, ...props }) => {
  return (
    <div className={`ui-card-header ${className}`} {...props}>
      {children}
    </div>
  )
}

/**
 * Card Body Component
 */
export const CardBody = ({ className = '', children, ...props }) => {
  return (
    <div className={`ui-card-body ${className}`} {...props}>
      {children}
    </div>
  )
}

/**
 * Card Footer Component
 */
export const CardFooter = ({ className = '', children, ...props }) => {
  return (
    <div className={`ui-card-footer ${className}`} {...props}>
      {children}
    </div>
  )
}

/**
 * Card Actions Component
 */
export const CardActions = ({ className = '', children, ...props }) => {
  return (
    <div className={`ui-card-actions ${className}`} {...props}>
      {children}
    </div>
  )
}

export default Card

