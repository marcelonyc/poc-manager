import { useState, useRef, useCallback, useMemo, useEffect } from 'react'
import {
    startOfWeek,
    endOfWeek,
    startOfMonth,
    endOfMonth,
    eachDayOfInterval,
    format,
    addWeeks,
    subWeeks,
    addMonths,
    subMonths,
    isSameMonth,
    isSameDay,
    parseISO,
    addDays,
    subDays,
    isAfter,
    isBefore,
    differenceInCalendarDays,
} from 'date-fns'

// ── Types ─────────────────────────────────────────────────────────────

export interface CalendarTask {
    id: number
    title: string
    description: string | null
    status?: string
    start_date?: string   // ISO date string
    due_date?: string     // ISO date string
    assignees?: { id: number; participant_name: string; participant_email: string }[]
    success_criteria_ids?: number[]
    groupId?: number      // set if this task belongs to a group
    groupTitle?: string   // name of the parent group
    isGroup?: boolean     // true if this represents a task group row
}

interface TaskCalendarProps {
    tasks: CalendarTask[]
    onTaskDateChange?: (taskId: number, startDate: string, dueDate: string, isGroup: boolean) => void
    onTaskClick?: (task: CalendarTask) => void
    readOnly?: boolean
    pocStartDate?: string
    pocEndDate?: string
}

// ── Color palette for task bars ─────────────────────────────────────

const STATUS_COLORS: Record<string, { bg: string; border: string; text: string }> = {
    not_started: { bg: 'bg-gray-300', border: 'border-gray-400', text: 'text-gray-800' },
    in_progress: { bg: 'bg-blue-400', border: 'border-blue-500', text: 'text-white' },
    completed: { bg: 'bg-green-400', border: 'border-green-500', text: 'text-white' },
    blocked: { bg: 'bg-red-400', border: 'border-red-500', text: 'text-white' },
    satisfied: { bg: 'bg-emerald-400', border: 'border-emerald-500', text: 'text-white' },
    partially_satisfied: { bg: 'bg-yellow-400', border: 'border-yellow-500', text: 'text-gray-900' },
    not_satisfied: { bg: 'bg-orange-400', border: 'border-orange-500', text: 'text-white' },
}

const GROUP_COLORS = [
    { bg: 'bg-indigo-400', border: 'border-indigo-500', text: 'text-white' },
    { bg: 'bg-purple-400', border: 'border-purple-500', text: 'text-white' },
    { bg: 'bg-teal-400', border: 'border-teal-500', text: 'text-white' },
    { bg: 'bg-pink-400', border: 'border-pink-500', text: 'text-white' },
    { bg: 'bg-cyan-400', border: 'border-cyan-500', text: 'text-white' },
    { bg: 'bg-amber-400', border: 'border-amber-500', text: 'text-gray-900' },
]

function getTaskColor(task: CalendarTask, index: number) {
    if (task.isGroup) {
        return GROUP_COLORS[index % GROUP_COLORS.length]
    }
    return STATUS_COLORS[task.status || 'not_started'] || STATUS_COLORS.not_started
}

// ── Date Slider Panel ───────────────────────────────────────────────

interface DateSliderPanelProps {
    task: CalendarTask
    rangeStart: Date
    rangeEnd: Date
    onDateChange: (taskId: number, startDate: string, endDate: string, isGroup: boolean) => void
    onClose: () => void
}

function DateSliderPanel({ task, rangeStart, rangeEnd, onDateChange, onClose }: DateSliderPanelProps) {
    const totalDays = differenceInCalendarDays(rangeEnd, rangeStart)

    const rawStart = task.start_date ? parseISO(task.start_date) : null
    const rawEnd = task.due_date ? parseISO(task.due_date) : null
    const currentStart = rawStart || rawEnd!
    const currentEnd = rawEnd || rawStart!

    const [startVal, setStartVal] = useState(
        Math.max(0, Math.min(totalDays, differenceInCalendarDays(currentStart, rangeStart)))
    )
    const [endVal, setEndVal] = useState(
        Math.max(0, Math.min(totalDays, differenceInCalendarDays(currentEnd, rangeStart)))
    )

    const startDate = addDays(rangeStart, startVal)
    const endDate = addDays(rangeStart, endVal)
    const duration = differenceInCalendarDays(endDate, startDate) + 1

    const handleStartChange = (val: number) => {
        const clamped = Math.min(val, endVal)
        setStartVal(clamped)
    }

    const handleEndChange = (val: number) => {
        const clamped = Math.max(val, startVal)
        setEndVal(clamped)
    }

    const handleApply = () => {
        onDateChange(task.id, format(startDate, 'yyyy-MM-dd'), format(endDate, 'yyyy-MM-dd'), !!task.isGroup)
        onClose()
    }

    const origStart = task.start_date || task.due_date || ''
    const origEnd = task.due_date || task.start_date || ''
    const hasChanged = format(startDate, 'yyyy-MM-dd') !== origStart ||
        format(endDate, 'yyyy-MM-dd') !== origEnd

    return (
        <div
            className="bg-gradient-to-r from-gray-50 to-slate-50 border-t border-gray-200 px-4 py-3 relative z-10"
            onClick={(e) => e.stopPropagation()}
        >
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span className="text-xs font-semibold text-gray-700">Adjust Dates</span>
                    <span className="text-xs text-gray-400">({duration} day{duration !== 1 ? 's' : ''})</span>
                </div>
                <button
                    onClick={onClose}
                    className="p-1 hover:bg-gray-200 rounded transition-colors text-gray-400 hover:text-gray-600"
                    title="Close"
                >
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <div className="space-y-3">
                <div>
                    <div className="flex justify-between items-center mb-1">
                        <span className="text-xs font-medium text-gray-500">Start Date</span>
                        <span className="text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                            {format(startDate, 'EEE, MMM d, yyyy')}
                        </span>
                    </div>
                    <input
                        type="range"
                        min={0}
                        max={totalDays}
                        value={startVal}
                        onChange={e => handleStartChange(+e.target.value)}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    />
                </div>
                <div>
                    <div className="flex justify-between items-center mb-1">
                        <span className="text-xs font-medium text-gray-500">End Date</span>
                        <span className="text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                            {format(endDate, 'EEE, MMM d, yyyy')}
                        </span>
                    </div>
                    <input
                        type="range"
                        min={0}
                        max={totalDays}
                        value={endVal}
                        onChange={e => handleEndChange(+e.target.value)}
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                    />
                </div>
            </div>
            <div className="flex justify-between items-center mt-3">
                <span className="text-[10px] text-gray-400">
                    Range: {format(rangeStart, 'MMM d')} — {format(rangeEnd, 'MMM d, yyyy')}
                </span>
                <div className="flex gap-2">
                    <button
                        onClick={onClose}
                        className="px-3 py-1 text-xs font-medium text-gray-600 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleApply}
                        disabled={!hasChanged}
                        className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${hasChanged
                            ? 'text-white bg-indigo-600 hover:bg-indigo-700'
                            : 'text-gray-400 bg-gray-100 cursor-not-allowed'
                            }`}
                    >
                        Apply
                    </button>
                </div>
            </div>
        </div>
    )
}

// ── Main Component ──────────────────────────────────────────────────

export default function TaskCalendar({
    tasks,
    onTaskDateChange,
    onTaskClick,
    readOnly = false,
    pocStartDate,
    pocEndDate,
}: TaskCalendarProps) {
    const [viewMode, setViewMode] = useState<'week' | 'month'>('month')
    const [currentDate, setCurrentDate] = useState(() => new Date())
    const [dragState, setDragState] = useState<{
        taskId: number
        isGroup: boolean
        edge: 'start' | 'end' | 'move'
        origStart: Date
        origEnd: Date
        startX: number
        dayWidth: number
    } | null>(null)
    const [dragPreview, setDragPreview] = useState<{
        taskId: number
        isGroup: boolean
        newStart: Date
        newEnd: Date
    } | null>(null)
    const gridRef = useRef<HTMLDivElement>(null)
    const [expandedTaskKey, setExpandedTaskKey] = useState<string | null>(null)

    // ── Derived date range ──────────────────────────────────────────

    const days = useMemo(() => {
        if (viewMode === 'week') {
            const start = startOfWeek(currentDate, { weekStartsOn: 1 })
            const end = endOfWeek(currentDate, { weekStartsOn: 1 })
            return eachDayOfInterval({ start, end })
        }
        // Month view: include surrounding days to fill the grid
        const monthStart = startOfMonth(currentDate)
        const monthEnd = endOfMonth(currentDate)
        const start = startOfWeek(monthStart, { weekStartsOn: 1 })
        const end = endOfWeek(monthEnd, { weekStartsOn: 1 })
        return eachDayOfInterval({ start, end })
    }, [viewMode, currentDate])

    // ── Schedulable tasks (those with at least one date) ────────────

    const scheduledTasks = useMemo(() => {
        return tasks.filter(t => t.start_date || t.due_date)
    }, [tasks])

    // ── Slider date range (extends visible range + POC bounds) ──────

    const sliderRange = useMemo(() => {
        let rangeStart = subDays(days[0], 14)
        let rangeEnd = addDays(days[days.length - 1], 14)
        if (pocStartDate) {
            const ps = parseISO(pocStartDate)
            if (isBefore(ps, rangeStart)) rangeStart = ps
        }
        if (pocEndDate) {
            const pe = parseISO(pocEndDate)
            if (isAfter(pe, rangeEnd)) rangeEnd = pe
        }
        for (const t of scheduledTasks) {
            if (t.start_date) {
                const d = parseISO(t.start_date)
                if (isBefore(d, rangeStart)) rangeStart = d
            }
            if (t.due_date) {
                const d = parseISO(t.due_date)
                if (isAfter(d, rangeEnd)) rangeEnd = d
            }
        }
        return { start: rangeStart, end: rangeEnd }
    }, [days, pocStartDate, pocEndDate, scheduledTasks])

    // Close slider panel when calendar view changes
    useEffect(() => {
        setExpandedTaskKey(null)
    }, [viewMode, currentDate])

    // ── Navigation ──────────────────────────────────────────────────

    const goBack = () => {
        setCurrentDate(prev => viewMode === 'week' ? subWeeks(prev, 1) : subMonths(prev, 1))
    }
    const goForward = () => {
        setCurrentDate(prev => viewMode === 'week' ? addWeeks(prev, 1) : addMonths(prev, 1))
    }
    const goToday = () => {
        setCurrentDate(new Date())
    }

    // ── Helpers ─────────────────────────────────────────────────────

    const dayIndex = (date: Date) => {
        return days.findIndex(d => isSameDay(d, date))
    }

    const clampDate = (d: Date, min?: Date, max?: Date) => {
        if (min && isBefore(d, min)) return min
        if (max && isAfter(d, max)) return max
        return d
    }

    // ── Drag handlers ───────────────────────────────────────────────

    const handleMouseDown = useCallback((
        e: React.MouseEvent,
        taskId: number,
        isGroup: boolean,
        edge: 'start' | 'end' | 'move',
        startDate: Date,
        endDate: Date,
    ) => {
        if (readOnly) return
        e.preventDefault()
        e.stopPropagation()

        const cell = gridRef.current?.querySelector('[data-day-cell]') as HTMLElement
        const dayWidth = cell ? cell.offsetWidth : 40

        setDragState({
            taskId,
            isGroup,
            edge,
            origStart: startDate,
            origEnd: endDate,
            startX: e.clientX,
            dayWidth,
        })
        setDragPreview({ taskId, isGroup, newStart: startDate, newEnd: endDate })
    }, [readOnly])

    useEffect(() => {
        if (!dragState) return

        const pocMin = pocStartDate ? parseISO(pocStartDate) : undefined
        const pocMax = pocEndDate ? parseISO(pocEndDate) : undefined

        const handleMouseMove = (e: MouseEvent) => {
            const dx = e.clientX - dragState.startX
            const dayDelta = Math.round(dx / dragState.dayWidth)
            if (dayDelta === 0 && dragState.edge !== 'move') {
                setDragPreview({ taskId: dragState.taskId, isGroup: dragState.isGroup, newStart: dragState.origStart, newEnd: dragState.origEnd })
                return
            }

            let newStart = dragState.origStart
            let newEnd = dragState.origEnd

            switch (dragState.edge) {
                case 'start':
                    newStart = addDays(dragState.origStart, dayDelta)
                    if (isAfter(newStart, newEnd)) newStart = newEnd
                    break
                case 'end':
                    newEnd = addDays(dragState.origEnd, dayDelta)
                    if (isBefore(newEnd, newStart)) newEnd = newStart
                    break
                case 'move': {
                    newStart = addDays(dragState.origStart, dayDelta)
                    newEnd = addDays(dragState.origEnd, dayDelta)
                    break
                }
            }

            // Clamp to POC range
            newStart = clampDate(newStart, pocMin, pocMax)
            newEnd = clampDate(newEnd, pocMin, pocMax)

            // Ensure start <= end
            if (isAfter(newStart, newEnd)) {
                if (dragState.edge === 'start') newStart = newEnd
                else newEnd = newStart
            }

            setDragPreview({ taskId: dragState.taskId, isGroup: dragState.isGroup, newStart, newEnd })
        }

        const handleMouseUp = () => {
            if (dragPreview && onTaskDateChange) {
                const startStr = format(dragPreview.newStart, 'yyyy-MM-dd')
                const endStr = format(dragPreview.newEnd, 'yyyy-MM-dd')
                const origStartStr = format(dragState.origStart, 'yyyy-MM-dd')
                const origEndStr = format(dragState.origEnd, 'yyyy-MM-dd')
                if (startStr !== origStartStr || endStr !== origEndStr) {
                    onTaskDateChange(dragState.taskId, startStr, endStr, dragState.isGroup)
                }
            }
            setDragState(null)
            setDragPreview(null)
        }

        window.addEventListener('mousemove', handleMouseMove)
        window.addEventListener('mouseup', handleMouseUp)
        return () => {
            window.removeEventListener('mousemove', handleMouseMove)
            window.removeEventListener('mouseup', handleMouseUp)
        }
    }, [dragState, dragPreview, onTaskDateChange, pocStartDate, pocEndDate])

    // ── Click vs Drag detection ─────────────────────────────────────

    const clickStartRef = useRef<{ x: number; y: number; time: number } | null>(null)

    const handleBarMouseDown = (
        e: React.MouseEvent,
        task: CalendarTask,
        startDate: Date,
        endDate: Date,
    ) => {
        clickStartRef.current = { x: e.clientX, y: e.clientY, time: Date.now() }
        handleMouseDown(e, task.id, !!task.isGroup, 'move', startDate, endDate)
    }

    const handleBarClick = (e: React.MouseEvent, task: CalendarTask) => {
        if (!clickStartRef.current) return
        const dx = Math.abs(e.clientX - clickStartRef.current.x)
        const dy = Math.abs(e.clientY - clickStartRef.current.y)
        const dt = Date.now() - clickStartRef.current.time
        // Only fire click if mouse barely moved and was quick
        if (dx < 5 && dy < 5 && dt < 300) {
            if (!readOnly) {
                const key = `${task.isGroup ? 'g' : 't'}-${task.id}`
                setExpandedTaskKey(prev => prev === key ? null : key)
            }
            onTaskClick?.(task)
        }
        clickStartRef.current = null
    }

    // ── Render task bar on the day grid ─────────────────────────────

    const renderTaskBar = (task: CalendarTask, taskIdx: number) => {
        const rawStart = task.start_date ? parseISO(task.start_date) : null
        const rawEnd = task.due_date ? parseISO(task.due_date) : null
        if (!rawStart && !rawEnd) return null

        const usedPreview = dragPreview && dragPreview.taskId === task.id && dragPreview.isGroup === !!task.isGroup
        const effectiveStart = usedPreview ? dragPreview!.newStart : (rawStart || rawEnd!)
        const effectiveEnd = usedPreview ? dragPreview!.newEnd : (rawEnd || rawStart!)

        const startIdx = dayIndex(effectiveStart)
        const endIdx = dayIndex(effectiveEnd)

        // Clip to visible range
        const visStartIdx = Math.max(0, startIdx)
        const visEndIdx = Math.min(days.length - 1, endIdx)
        if (visStartIdx > days.length - 1 || visEndIdx < 0) return null

        const span = visEndIdx - visStartIdx + 1
        const color = getTaskColor(task, taskIdx)
        const isDragging = !!usedPreview

        return (
            <div
                key={`${task.isGroup ? 'g' : 't'}-${task.id}`}
                className="relative flex items-center"
                style={{ height: '28px' }}
            >
                {/* Full grid width row for positioning */}
                <div className="absolute inset-0" style={{
                    display: 'grid',
                    gridTemplateColumns: `repeat(${days.length}, 1fr)`,
                }}>
                    {/* Task bar */}
                    <div
                        className={`
                            relative
                            ${color.bg} ${color.text} ${color.border}
                            border rounded-md text-xs font-medium
                            truncate flex items-center px-1.5
                            ${readOnly ? 'cursor-pointer' : 'cursor-grab'}
                            ${isDragging ? 'opacity-80 shadow-lg ring-2 ring-blue-300' : 'hover:shadow-md'}
                            transition-shadow select-none
                        `}
                        style={{
                            gridColumnStart: visStartIdx + 1,
                            gridColumnEnd: visStartIdx + span + 1,
                            height: '24px',
                            marginTop: '2px',
                        }}
                        onMouseDown={(e) => {
                            if (e.button !== 0) return
                            handleBarMouseDown(e, task, effectiveStart, effectiveEnd)
                        }}
                        onMouseUp={(e) => handleBarClick(e, task)}
                        title={`${task.title}${task.groupTitle ? ` (${task.groupTitle})` : ''}`}
                    >
                        {/* Drag handle - left edge */}
                        {!readOnly && (
                            <div
                                className="absolute left-0 top-0 bottom-0 w-3 cursor-col-resize z-10 group/left rounded-l-md"
                                onMouseDown={(e) => {
                                    e.stopPropagation()
                                    handleMouseDown(e, task.id, !!task.isGroup, 'start', effectiveStart, effectiveEnd)
                                }}
                            >
                                <div className="absolute inset-y-1 left-0.5 w-1 rounded-full bg-black/0 group-hover/left:bg-black/20 transition-colors" />
                            </div>
                        )}

                        <span className="truncate text-[11px] leading-tight pl-2 pr-2">
                            {task.isGroup ? '📁 ' : ''}{task.title}
                        </span>

                        {/* Drag handle - right edge */}
                        {!readOnly && (
                            <div
                                className="absolute right-0 top-0 bottom-0 w-3 cursor-col-resize z-10 group/right rounded-r-md"
                                onMouseDown={(e) => {
                                    e.stopPropagation()
                                    handleMouseDown(e, task.id, !!task.isGroup, 'end', effectiveStart, effectiveEnd)
                                }}
                            >
                                <div className="absolute inset-y-1 right-0.5 w-1 rounded-full bg-black/0 group-hover/right:bg-black/20 transition-colors" />
                            </div>
                        )}
                    </div>
                </div>
            </div>
        )
    }

    // ── Render ───────────────────────────────────────────────────────

    const headerLabel = viewMode === 'week'
        ? `${format(days[0], 'MMM d')} – ${format(days[days.length - 1], 'MMM d, yyyy')}`
        : format(currentDate, 'MMMM yyyy')

    return (
        <div className="space-y-3">
            {/* Toolbar */}
            <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2">
                    <button
                        onClick={goBack}
                        className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 text-gray-600"
                        title="Previous"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
                    </button>
                    <h3 className="text-lg font-semibold text-gray-900 min-w-[200px] text-center">
                        {headerLabel}
                    </h3>
                    <button
                        onClick={goForward}
                        className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 text-gray-600"
                        title="Next"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                    </button>
                    <button
                        onClick={goToday}
                        className="px-3 py-1.5 text-sm rounded-lg border border-gray-300 hover:bg-gray-50 text-gray-600 ml-1"
                    >
                        Today
                    </button>
                </div>

                <div className="flex rounded-lg border border-gray-300 overflow-hidden">
                    <button
                        onClick={() => setViewMode('week')}
                        className={`px-4 py-1.5 text-sm font-medium transition-colors ${viewMode === 'week'
                            ? 'bg-indigo-600 text-white'
                            : 'bg-white text-gray-600 hover:bg-gray-50'
                            }`}
                    >
                        Week
                    </button>
                    <button
                        onClick={() => setViewMode('month')}
                        className={`px-4 py-1.5 text-sm font-medium transition-colors ${viewMode === 'month'
                            ? 'bg-indigo-600 text-white'
                            : 'bg-white text-gray-600 hover:bg-gray-50'
                            }`}
                    >
                        Month
                    </button>
                </div>
            </div>

            {/* Calendar Legend */}
            <div className="flex flex-wrap gap-3 text-xs text-gray-600">
                <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-gray-300 inline-block" /> Not Started</span>
                <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-blue-400 inline-block" /> In Progress</span>
                <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-green-400 inline-block" /> Completed</span>
                <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-red-400 inline-block" /> Blocked</span>
                {!readOnly && <span className="text-gray-400 ml-2">• Drag edges to resize, drag bar to move, click for date sliders</span>}
            </div>

            {/* Day header row */}
            <div ref={gridRef} className="border border-gray-200 rounded-lg overflow-hidden">
                <div
                    className="grid bg-gray-50 border-b border-gray-200"
                    style={{ gridTemplateColumns: `repeat(${days.length}, 1fr)` }}
                >
                    {days.map((day, i) => {
                        const isToday = isSameDay(day, new Date())
                        const isCurrentMonth = isSameMonth(day, currentDate)
                        return (
                            <div
                                key={i}
                                data-day-cell
                                className={`
                                    text-center py-2 text-xs border-r border-gray-200 last:border-r-0
                                    ${isToday ? 'bg-indigo-50 font-bold text-indigo-700' : ''}
                                    ${!isCurrentMonth && viewMode === 'month' ? 'text-gray-400' : 'text-gray-700'}
                                `}
                            >
                                <div className="font-medium">{format(day, viewMode === 'week' ? 'EEE' : 'EEE')}</div>
                                <div className={`text-sm ${isToday ? 'bg-indigo-600 text-white rounded-full w-6 h-6 flex items-center justify-center mx-auto' : ''}`}>
                                    {format(day, 'd')}
                                </div>
                            </div>
                        )
                    })}
                </div>

                {/* Task rows */}
                <div className="bg-white divide-y divide-gray-100 min-h-[100px]">
                    {scheduledTasks.length === 0 ? (
                        <div className="text-center text-gray-400 py-12 text-sm">
                            No tasks with dates to display. Add start/due dates to your tasks to see them here.
                        </div>
                    ) : (
                        scheduledTasks.map((task, idx) => (
                            <div key={`${task.isGroup ? 'g' : 't'}-${task.id}`} className="relative" style={{ minHeight: '32px' }}>
                                {/* Vertical gridlines */}
                                <div
                                    className="absolute inset-0 pointer-events-none"
                                    style={{
                                        display: 'grid',
                                        gridTemplateColumns: `repeat(${days.length}, 1fr)`,
                                    }}
                                >
                                    {days.map((day, i) => (
                                        <div
                                            key={i}
                                            className={`border-r border-gray-100 last:border-r-0 ${isSameDay(day, new Date()) ? 'bg-indigo-50/30' : ''}`}
                                        />
                                    ))}
                                </div>
                                {renderTaskBar(task, idx)}
                                {/* Date slider panel */}
                                {!readOnly && expandedTaskKey === `${task.isGroup ? 'g' : 't'}-${task.id}` && onTaskDateChange && (
                                    <DateSliderPanel
                                        key={`slider-${task.isGroup ? 'g' : 't'}-${task.id}`}
                                        task={task}
                                        rangeStart={sliderRange.start}
                                        rangeEnd={sliderRange.end}
                                        onDateChange={onTaskDateChange}
                                        onClose={() => setExpandedTaskKey(null)}
                                    />
                                )}
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Unscheduled tasks note */}
            {tasks.filter(t => !t.start_date && !t.due_date).length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-800">
                    <strong>{tasks.filter(t => !t.start_date && !t.due_date).length} task(s)</strong> without dates are not shown on the calendar.
                    {tasks.filter(t => !t.start_date && !t.due_date).map(t => (
                        <span
                            key={`${t.isGroup ? 'g' : 't'}-${t.id}`}
                            className="inline-block ml-2 px-2 py-0.5 bg-yellow-100 rounded text-xs cursor-pointer hover:bg-yellow-200"
                            onClick={() => onTaskClick?.(t)}
                        >
                            {t.title}
                        </span>
                    ))}
                </div>
            )}
        </div>
    )
}
