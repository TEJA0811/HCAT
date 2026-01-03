import { Team } from '../../teams/entities/team.entity';
import { UserType } from '../../utils/constant';
import { Entity, PrimaryGeneratedColumn, Column, BaseEntity, ManyToOne, JoinColumn, ManyToMany, CreateDateColumn, OneToMany } from 'typeorm';
import { Project } from '../../projects/entities/project.entity';
import { Manager } from '../../managers/entities/manager.entity';
import { Task } from '../../tasks/entities/task.entity';

@Entity({ name: 'users' })
export class User extends BaseEntity {
  @PrimaryGeneratedColumn({ type: 'bigint' })
  id: number;

  @Column({ length: 70 })
  name: string;

  @Column({ unique: true })
  email: string;

  @Column({ length: 70 })
  password: string;

  @Column({ type: 'enum', enum: UserType })
  role: UserType;

  @Column({ type: 'bigint' })
  reports_to: Number;

  @Column({ type: 'bigint' })
  team_id: number;

  @Column({ type: 'bigint', nullable: true })
  project_id: number;

  @Column()
  @CreateDateColumn()
  joining_date: Date;

   // Many users belong to one team
  @ManyToOne(() => Team, (team) => team.users)
  @JoinColumn({ name: 'team_id' })
  team: Team;

  // Many users belong to one project
  @ManyToOne(() => Project, (project) => project.users)
  @JoinColumn({ name: 'project_id' })
  project: Project;

    // Many users belong to one Manager
  @ManyToOne(() => Manager, (manager) => manager.users)
  @JoinColumn({ name: 'reports_to' })
  manager: Manager;

    // one user has many tasks
  @OneToMany(() => Task, (task) => task.assignee)
  tasks: Task[];
  
}
