import { describe, expect, it } from 'vitest'
import { formatApiErrorDetail, toUserErrorMessage } from './apiError.js'

describe('formatApiErrorDetail', () => {
  it('summarises FastAPI 422 validation objects instead of stringifying them', () => {
    const detail = [
      { loc: ['body', 'data', 'day'], msg: 'Value error, day is required' },
      { loc: ['body', 'data', 'month'], msg: 'Value error, month is required' },
      { loc: ['body', 'data', 'year'], msg: 'Value error, year is required' },
      { loc: ['body', 'data', 'hour'], msg: 'Value error, hour is required' },
      { loc: ['body', 'data', 'minute'], msg: 'Value error, minute is required' },
      { loc: ['body', 'data', 'lat'], msg: 'Value error, lat is required' },
      { loc: ['body', 'data', 'lng'], msg: 'Value error, lng is required' },
    ]

    expect(formatApiErrorDetail(detail, 422)).toBe(
      'Enter the missing birth data: Day, Month, Year, Hour, Minute, Latitude, and Longitude.',
    )
  })

  it('keeps a single required-field error specific', () => {
    expect(
      formatApiErrorDetail([{ loc: ['body', 'data', 'year'], msg: 'Field required' }], 422),
    ).toBe('Year is required.')
  })
})

describe('toUserErrorMessage', () => {
  it('strips Electron IPC wrapping and object-stringified FastAPI details', () => {
    expect(
      toUserErrorMessage(
        new Error(
          "Error invoking remote method 'api-request': Error: HTTP 422: [object Object],[object Object]",
        ),
        'Could not generate the chart.',
      ),
    ).toBe('Could not generate the chart.')
  })
})
