<template>
  <div class="highlight-container highlight-container--bottom-labels" @click="open" @touchend="open">
    <entity-item
      v-for="(chunk, i) in chunks"
      :key="i"
      :lid="chunk.id"
      :content="chunk.text"
      :newline="chunk.newline"
      :label="chunk.label"
      :color="chunk.color"
      :labels="labels"
      @remove="deleteAnnotation(chunk.id)"
      @update="updateEntity($event.id, chunk.id)"
    />
    <v-menu
      v-model="showMenu"
      :position-x="x"
      :position-y="y"
      absolute
      offset-y
      style=""
    >
      <v-list
        dense
        min-width="150"
        max-height="400"
        class="overflow-y-auto"
      >
        <v-list-item
          v-for="(label, i) in labels"
          :key="i"
          v-shortkey="[label.suffix_key]"
          @shortkey="assignLabel(label.id)"
          @click="assignLabel(label.id)"
        >
          <v-list-item-content>
            <v-list-item-title v-text="label.text" />
          </v-list-item-content>
          <v-list-item-action>
            <v-list-item-action-text v-text="label.suffix_key" />
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script>
import EntityItem from '~/components/molecules/EntityItem'
import lodash from 'lodash'
import '~/plugins/jsplumb.js'
import { easyFlowMixin } from '~/plugins/mixins.js'

export default {
  components: {
    EntityItem
  },
  props: {
    text: {
      type: String,
      default: '',
      required: true
    },
    labels: {
      type: Array,
      default: () => ([]),
      required: true
    },
    entities: {
      type: Array,
      default: () => ([]),
      required: true
    },
    deleteAnnotation: {
      type: Function,
      default: () => ([]),
      required: true
    },
    updateEntity: {
      type: Function,
      default: () => ([]),
      required: true
    },
    addEntity: {
      type: Function,
      default: () => ([]),
      required: true
    }
  },
  data() {
    return {
      showMenu: false,
      x: 0,
      y: 0,
      start: 0,
      end: 0,
      jsPlumb: null,
      conn: []
    }
  },

  computed: {
    sortedEntities() {
      return this.entities.slice().sort((a, b) => a.start_offset - b.start_offset)
    },

    chunks() {
      let chunks = []
      const entities = this.sortedEntities
      let startOffset = 0
      for (const entity of entities) {
        // add non-entities to chunks.
        chunks = chunks.concat(this.makeChunks(this.text.slice(startOffset, entity.start_offset)))
        startOffset = entity.end_offset

        // add entities to chunks.
        const label = this.labelObject[entity.label]
        chunks.push({
          id: entity.id,
          label: label.text,
          color: label.background_color,
          text: this.text.slice(entity.start_offset, entity.end_offset)
        })
      }
      // add the rest of text.
      chunks = chunks.concat(this.makeChunks(this.text.slice(startOffset, this.text.length)))

      // 加载连线
      this.$nextTick(() => {
        this.loadNode()
      })

      return chunks
    },

    labelObject() {
      const obj = {}
      for (const label of this.labels) {
        obj[label.id] = label
      }
      return obj
    }
  },
  
  mixins: [easyFlowMixin],

  methods: {
    loadNode() {
      if (this.jsPlumb != null) {
        this.jsPlumb.deleteEveryEndpoint()
      }
      this.conn = []
      for (let i = 0; i < this.entities.length; i++) {
        const node = this.entities[i]
        let connections = node.connections.split(",")
        for (var j = 0; j < connections.length && connections[j] !== ""; j++) {
          this.conn.push({from: String(node.id), to: connections[j]})
        }
      }
      this.$nextTick(() => {
        this.jsPlumb = jsPlumb.getInstance()
          this.$nextTick(() => {
            this.jsPlumbInit()
        })
      })
    },

    jsPlumbInit() {
      this.jsPlumb.ready(() => {
        // 导入默认配置
        this.jsPlumb.importDefaults(this.jsplumbSetting)
        // 会使整个jsPlumb立即重绘。
        this.jsPlumb.setSuspendDrawing(false, true)
        // 初始化节点
        this.loadLine()
        // 连线
        this.jsPlumb.bind("connection", (evt) => {
          let from = evt.source.id
          let to = evt.target.id
          this.addConnection(from, to)
        })
        // 双击连线 删除
        this.jsPlumb.bind('dblclick', (evt, originalEvent) => {
          this.jsPlumb.deleteConnection(evt)
          this.deleteConnection(evt.sourceId, evt.targetId)
        })
        // 连线
        this.jsPlumb.bind("beforeDrop", (evt) => {
          let from = evt.sourceId
          let to = evt.targetId
          if (from === to) {
            return false
          }
          if (this.hasLine(from, to)) {
            return false
          }
          if (this.hashOppositeLine(from, to)) {
            return false
          }
          return true
        })
      })
    },
    // 添加连线
    addConnection(from, to) {
      this.conn.push({from: from, to: to})
      for (var i = 0; i < this.entities.length; i++){
        let node = this.entities[i]
        if (from === String(node.id)) {
          if (node.connections === ""){
            this.$emit('updateEntityConn', node.id, to)
          } else {
            this.$emit('updateEntityConn', node.id, node.connections + ',' + to)
          }
          break
        }
      }
    },
    // 删除线
    deleteConnection(from, to) {
      for (var i = 0; i < this.entities.length; i++){
        let node = this.entities[i]
        if (from === String(node.id)) {
          let connections = node.connections.replace(to, "")
          connections = connections.replace(",,", ",")
          if (connections[0] == ',') {
            connections = connections.slice(1)
          }
          if (connections[connections.length-1] == ',') {
            connections = connections.slice(0,-1)
          }
          this.$emit('updateEntityConn', node.id, connections)
          break
        }
      }
      this.conn = this.conn.filter(function (line) {
          if (line.from == from && line.to == to) {
              return false
          }
          return true
      })
    },
    // 加载线
    loadLine() {
      // 设置为节点
      for (var i = 0; i < this.entities.length; i++){
        let node = this.entities[i]
        // 设置源点，可以拖出线连接其他节点
        this.jsPlumb.makeSource(String(node.id), lodash.merge(this.jsplumbSourceOptions, {}))
        // 设置目标点，其他源点拖出的线可以连接该节点
        this.jsPlumb.makeTarget(String(node.id), this.jsplumbTargetOptions)
      }
      // 初始化连线
      for (var i = 0; i < this.conn.length; i++){
        let node = this.conn[i]
        var params = {
          source: node.from,
          target: node.to
        }
        this.jsPlumb.connect(params, this.jsplumbConnectOptions)
      }
    },
    // 是否具有该线
    hasLine(from, to) {
      for (var i = 0; i < this.conn.length; i++) {
        var line = this.conn[i]
        if (line.from === from && line.to === to) {
          return true
        }
      }
      return false
    },
    // 是否含有相反的线
    hashOppositeLine(from, to) {
      return this.hasLine(to, from)
    },

    makeChunks(text) {
      const chunks = []
      const snippets = text.split('\n')
      for (const snippet of snippets.slice(0, -1)) {
        chunks.push({
          label: null,
          color: null,
          text: snippet + '\n',
          newline: false
        })
        chunks.push({
          label: null,
          color: null,
          text: '',
          newline: true
        })
      }
      chunks.push({
        label: null,
        color: null,
        text: snippets.slice(-1)[0],
        newline: false
      })
      return chunks
    },
    show(e) {
      e.preventDefault()
      this.showMenu = false
      this.x = e.clientX || e.changedTouches[0].clientX
      this.y = e.clientY || e.changedTouches[0].clientY
      this.$nextTick(() => {
        this.showMenu = true
      })
    },
    setSpanInfo() {
      let selection
      // Modern browsers.
      if (window.getSelection) {
        selection = window.getSelection()
      } else if (document.selection) {
        selection = document.selection
      }
      // If nothing is selected.
      if (selection.rangeCount <= 0) {
        return
      }
      const range = selection.getRangeAt(0)
      const preSelectionRange = range.cloneRange()
      preSelectionRange.selectNodeContents(this.$el)
      preSelectionRange.setEnd(range.startContainer, range.startOffset)
      this.start = [...preSelectionRange.toString()].length
      this.end = this.start + [...range.toString()].length
    },
    validateSpan() {
      if ((typeof this.start === 'undefined') || (typeof this.end === 'undefined')) {
        return false
      }
      if (this.start === this.end) {
        return false
      }
      for (const entity of this.entities) {
        if ((entity.start_offset <= this.start) && (this.start < entity.end_offset)) {
          return false
        }
        if ((entity.start_offset < this.end) && (this.end <= entity.end_offset)) {
          return false
        }
        if ((this.start < entity.start_offset) && (entity.end_offset < this.end)) {
          return false
        }
      }
      return true
    },
    open(e) {
      this.setSpanInfo()
      if (this.validateSpan()) {
        this.show(e)
      }
    },
    assignLabel(labelId) {
      if (this.validateSpan()) {
        this.addEntity(this.start, this.end, labelId)
        this.showMenu = false
        this.start = 0
        this.end = 0
      }
    }
  }
}
</script>

<style scoped>
.highlight-container.highlight-container--bottom-labels {
  align-items: flex-start;
}
.highlight-container {
  line-height: 42px!important;
  display: flex;
  flex-wrap: wrap;
  white-space: pre-wrap;
  cursor: default;
}
.highlight-container.highlight-container--bottom-labels .highlight.bottom {
  margin-top: 6px;
}
</style>
