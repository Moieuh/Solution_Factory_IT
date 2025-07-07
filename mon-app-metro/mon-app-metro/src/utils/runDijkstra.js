export default function runDijkstraTimeAware(nodes, edges, startId, endId, startTime = 0) {
  console.log("🧠 Dijkstra start:", startId, "→", endId)
  const arrivalTimes = {}
  const prev = {}
  const visited = new Set()

  for (const node of nodes) {
    arrivalTimes[node.id] = Infinity
    prev[node.id] = null
  }
  arrivalTimes[startId] = startTime

  while (visited.size < nodes.length) {
    let current = null
    for (const node of nodes) {
      if (!visited.has(node.id) && (current === null || arrivalTimes[node.id] < arrivalTimes[current])) {
        current = node.id
      }
    }

    if (!current || arrivalTimes[current] === Infinity) break
    if (current === endId) break

    visited.add(current)

    const outgoingEdges = edges.filter(e => e.from === current)
    for (const edge of outgoingEdges) {
      const { to, duration, departure, type } = edge
      if (visited.has(to)) continue

      const currentArrival = arrivalTimes[current]
      let waitTime = 0

      if (type === 'transfer') {
        waitTime = 0
      } else if (departure !== undefined) {
        waitTime = Math.max(0, departure - currentArrival)
      }

      const arrivalCandidate = currentArrival + waitTime + duration
      if (arrivalCandidate < arrivalTimes[to]) {
        arrivalTimes[to] = arrivalCandidate
        prev[to] = current
      }
    }
  }

  const path = []
  const steps = []
  let u = endId

  while (u !== null && prev[u]) {
    const from = prev[u]
    const to = u

    const edgeUsed = edges.find(e => e.from === from && e.to === to)

    steps.unshift({
      from,
      to,
      line: edgeUsed?.line || '?',
      type: edgeUsed?.type || 'ride',
      arrival: arrivalTimes[to]
    })

    path.unshift(to)
    u = from
  }

  if (startId === endId && arrivalTimes[endId] < Infinity) {
    path.push(startId)
  } else {
    path.unshift(startId)
  }

  return {
    path,
    total: arrivalTimes[endId],
    steps
  }
}
